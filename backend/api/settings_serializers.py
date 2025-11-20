"""
Serializers for Settings API
"""
from rest_framework import serializers
from .settings_models import BusinessProfile, PaymentProviderConfig
from .models import UserProfile


class BusinessProfileSerializer(serializers.ModelSerializer):
    """Serializer for business profile settings"""
    
    class Meta:
        model = BusinessProfile
        fields = [
            'id', 'company_name', 'business_phone', 'business_type', 
            'country', 'business_email', 'business_address', 'tax_id', 
            'website', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (for backward compatibility)"""
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'email', 'company_name', 'country', 'phone_number', 
            'business_type', 'developer_type', 'preferred_currency',
            'kyc_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['kyc_verified', 'created_at', 'updated_at']


class PaymentProviderConfigSerializer(serializers.ModelSerializer):
    """Serializer for payment provider configuration"""
    public_key = serializers.CharField(write_only=True, required=False)
    secret_key = serializers.CharField(write_only=True, required=False)
    public_key_masked = serializers.SerializerMethodField()
    secret_key_masked = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentProviderConfig
        fields = [
            'id', 'provider', 'mode', 'is_active', 'is_primary',
            'public_key', 'secret_key', 'public_key_masked', 'secret_key_masked',
            'credentials_validated', 'last_validated_at', 'validation_error',
            'webhook_url', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'credentials_validated', 'last_validated_at', 
            'validation_error', 'created_at', 'updated_at'
        ]
    
    def get_public_key_masked(self, obj):
        """Return masked public key"""
        return obj.get_masked_public_key()
    
    def get_secret_key_masked(self, obj):
        """Return masked secret key"""
        return obj.get_masked_secret_key()
    
    def create(self, validated_data):
        """Create provider config with encrypted keys"""
        public_key = validated_data.pop('public_key', None)
        secret_key = validated_data.pop('secret_key', None)
        
        instance = PaymentProviderConfig(**validated_data)
        
        if public_key:
            instance.set_public_key(public_key)
        if secret_key:
            instance.set_secret_key(secret_key)
        
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        """Update provider config with encrypted keys"""
        public_key = validated_data.pop('public_key', None)
        secret_key = validated_data.pop('secret_key', None)
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update encrypted fields if provided
        if public_key:
            instance.set_public_key(public_key)
        if secret_key:
            instance.set_secret_key(secret_key)
        
        instance.save()
        return instance


class PaymentProviderConfigDetailSerializer(PaymentProviderConfigSerializer):
    """Detailed serializer that includes decrypted keys (for validation only)"""
    public_key_decrypted = serializers.SerializerMethodField()
    secret_key_decrypted = serializers.SerializerMethodField()
    
    class Meta(PaymentProviderConfigSerializer.Meta):
        fields = PaymentProviderConfigSerializer.Meta.fields + [
            'public_key_decrypted', 'secret_key_decrypted'
        ]
    
    def get_public_key_decrypted(self, obj):
        """Return decrypted public key (use with caution)"""
        return obj.get_public_key()
    
    def get_secret_key_decrypted(self, obj):
        """Return decrypted secret key (use with caution)"""
        return obj.get_secret_key()
