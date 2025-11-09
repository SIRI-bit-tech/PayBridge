from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import (
    UserProfile, APIKey, PaymentProvider, Transaction, 
    Webhook, Subscription, AuditLog, KYCVerification,
    Invoice, UsageMetric, WebhookEvent, CURRENCY_CHOICES
)
import phonenumbers


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['email', 'first_name', 'last_name', 'company_name', 'country', 'phone_number', 'business_type', 'developer_type', 'preferred_currency', 'kyc_verified']


class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=True, source='firstname')
    last_name = serializers.CharField(max_length=150, required=True, source='lastname')
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(max_length=20, required=True)
    country = serializers.CharField(max_length=2, required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    company_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    developer_type = serializers.ChoiceField(choices=UserProfile.DEVELOPER_TYPE_CHOICES, required=False, allow_blank=True)
    preferred_currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, required=False)
    terms_accepted = serializers.BooleanField(required=True)
    
    def to_internal_value(self, data):
        # Convert string 'true'/'false' to boolean if needed
        if 'terms_accepted' in data and isinstance(data['terms_accepted'], str):
            data = data.copy()
            data['terms_accepted'] = data['terms_accepted'].lower() == 'true'
        return super().to_internal_value(data)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_phone_number(self, value):
        try:
            # Get the country from the request context if available
            request = self.context.get('request')
            country = None
            if request and hasattr(request, 'data') and 'country' in request.data:
                country = request.data['country']
            
            # If it's a Nigerian number starting with 234, ensure it's in the correct format
            if value.startswith('234') and len(value) == 13:
                # Convert to international format for validation
                intl_format = f"+{value}"
                parsed = phonenumbers.parse(intl_format, None)
                if not phonenumbers.is_valid_number(parsed):
                    raise serializers.ValidationError("Invalid Nigerian phone number format. Please use format: 234XXXXXXXXXX")
                # Return E.164 format
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            
            # For numbers that are all digits but don't start with '+', handle based on country
            if value.isdigit() and not value.startswith('+'):
                if country:
                    # Use the country from the request to parse the number
                    parsed = phonenumbers.parse(value, country)
                else:
                    # If no country provided, assume it's a local number in the default region
                    parsed = phonenumbers.parse(value, 'US')  # Default to US if no country specified
            else:
                # For numbers with '+' or other formats, parse as is
                parsed = phonenumbers.parse(value, None)
            
            if not phonenumbers.is_valid_number(parsed):
                raise serializers.ValidationError(
                    "Invalid phone number format. Please use international format: +[country code][number]"
                )
            
            # Always return in E.164 format
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            
        except phonenumbers.NumberParseException as e:
            raise serializers.ValidationError(f"Invalid phone number format: {str(e)}")
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        if not attrs.get('terms_accepted'):
            raise serializers.ValidationError({"terms_accepted": "You must accept the terms of service."})
        return attrs
    
    def create(self, validated_data):
        # Remove fields not needed for User creation
        confirm_password = validated_data.pop('confirm_password')
        terms_accepted = validated_data.pop('terms_accepted')
        company_name = validated_data.pop('company_name', '')
        developer_type = validated_data.pop('developer_type', '')
        preferred_currency = validated_data.pop('preferred_currency', 'USD')
        country = validated_data.pop('country')
        phone_number = validated_data.pop('phone_number')
        
        # Create User
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('firstname', ''),  # Use get with default to avoid KeyError
            last_name=validated_data.get('lastname', ''),    # Use get with default to avoid KeyError
            is_active=True  # Auto-activate users (email verification optional)
        )
        
        # Create or update UserProfile
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'company_name': company_name,
                'country': country,
                'phone_number': phone_number,
                'developer_type': developer_type,
                'preferred_currency': preferred_currency
            }
        )
        
        return user


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'key', 'status', 'last_used', 'created_at']
        read_only_fields = ['id', 'key', 'secret', 'last_used', 'created_at']


class PaymentProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProvider
        fields = ['id', 'provider', 'is_live', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'amount', 'currency', 'status', 
            'provider', 'customer_email', 'description', 'fee', 
            'net_amount', 'created_at'
        ]
        read_only_fields = ['id', 'reference', 'fee', 'net_amount', 'created_at']


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = ['id', 'url', 'event_types', 'is_active', 'last_triggered', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['plan', 'status', 'current_period_start', 'current_period_end', 'renewal_date']
        read_only_fields = ['status', 'current_period_start', 'current_period_end', 'renewal_date']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['action', 'ip_address', 'user_agent', 'details', 'created_at']
        read_only_fields = ['action', 'ip_address', 'user_agent', 'details', 'created_at']

class KYCVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCVerification
        fields = ['id', 'verification_type', 'verification_id', 'status', 'provider', 'verified_at', 'created_at']
        read_only_fields = ['id', 'status', 'verified_at', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'status', 'amount', 'tax', 'total', 'due_date', 'paid_date', 'created_at']
        read_only_fields = ['id', 'invoice_number', 'created_at']


class UsageMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageMetric
        fields = ['id', 'period_start', 'period_end', 'api_calls', 'transaction_volume', 'data_transferred_mb', 'cost']
        read_only_fields = ['id', 'api_calls', 'transaction_volume', 'data_transferred_mb', 'cost']


class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = ['id', 'event_type', 'status', 'response_status_code', 'attempt', 'created_at']
        read_only_fields = ['id', 'created_at']
