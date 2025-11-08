import logging
from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import requests
import hmac
import hashlib
from decimal import Decimal
from datetime import timedelta

from .models import (
    UserProfile, APIKey, PaymentProvider, Transaction,
    Webhook, Subscription, AuditLog, KYCVerification,
    Invoice, UsageMetric
)
from .serializers import (
    UserProfileSerializer, APIKeySerializer, PaymentProviderSerializer,
    TransactionSerializer, WebhookSerializer, SubscriptionSerializer,
    AuditLogSerializer, KYCVerificationSerializer, InvoiceSerializer,
    UsageMetricSerializer, RegistrationSerializer
)
from .permissions import IsOwner
from .kyc_service import KYCService
from .analytics_service import AnalyticsService
from .billing_service import BillingService
from .payment_service import PaymentService
from .exceptions import KYCVerificationFailed, InvalidAPIKey
from .tasks import process_transaction_webhook
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(TokenObtainPairView):
    """
    Custom login view that supports both email and phone number login
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        identifier = request.data.get('email') or request.data.get('phone_number')
        password = request.data.get('password')
        remember_me = request.data.get('remember_me', False)

        if not identifier or not password:
            return Response(
                {'error': 'Email/Phone and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find user by email or phone
        user = None
        if '@' in identifier:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                pass
        else:
            try:
                # Look up user by phone number through UserProfile
                profile = UserProfile.objects.get(phone_number=identifier)
                user = profile.user
            except (UserProfile.DoesNotExist, UserProfile.MultipleObjectsReturned):
                pass

        if not user or not user.check_password(password):
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate tokens with expiration based on remember_me
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        if remember_me:
            # Set expiration to 30 days for both tokens when remember_me is True
            refresh['exp'] = timezone.now() + timedelta(days=30)
            access_token['exp'] = timezone.now() + timedelta(days=30)
        
        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'phone_number': user.profile.phone_number if hasattr(user, 'profile') else '',
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                
                # Send email verification link
                self._send_verification_email(user)
                
                return Response({
                    'message': 'Account created successfully. Please check your email to verify your account.',
                    'user_id': user.id
                }, status=status.HTTP_201_CREATED)
                
            except IntegrityError as e:
                logger.error(f'Database error during registration: {str(e)}', exc_info=True)
                return Response(
                    {'error': 'A user with this email or phone number already exists.'},
                    status=status.HTTP_409_CONFLICT
                )
            except (DRFValidationError, DjangoValidationError) as e:
                logger.warning(f'Validation error during registration: {str(e)}')
                return Response(
                    {'error': 'Invalid registration data', 'details': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.error(f'Unexpected error during registration: {str(e)}', exc_info=True)
                return Response(
                    {'error': 'An unexpected error occurred during registration. Please try again later.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def _send_verification_email(self, user):
        """Send verification email to the user"""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        subject = 'Verify your email address'
        context = {
            'user': user,
            'uid': uid,
            'token': token,
            'domain': settings.FRONTEND_URL,
        }
        
        message = render_to_string('emails/email_verification.html', context)
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message,
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f'Failed to send verification email: {str(e)}', exc_info=True)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email_or_phone = request.data.get('email_or_phone')
        if not email_or_phone:
            return Response(
                {'error': 'Email or phone number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Try to find user by email or phone
            if '@' in email_or_phone:
                user = User.objects.get(email=email_or_phone)
            else:
                # Look up user by phone number through UserProfile
                profile = UserProfile.objects.get(phone_number=email_or_phone)
                user = profile.user
            
            self._send_password_reset_email(user)
            
            return Response({
                'message': 'If your email/phone exists in our system, you will receive a password reset link.'
            })
            
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            # Don't reveal that the user doesn't exist
            return Response({
                'message': 'If your email/phone exists in our system, you will receive a password reset link.'
            })
            
        except (User.MultipleObjectsReturned, UserProfile.MultipleObjectsReturned):
            # Handle case where multiple users are found (shouldn't happen with proper constraints)
            return Response({
                'message': 'If your email/phone exists in our system, you will receive a password reset link.'
            })
    
    def _send_password_reset_email(self, user):
        """Send password reset email to the user"""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        subject = 'Password Reset Request'
        context = {
            'user': user,
            'uid': uid,
            'token': token,
            'domain': settings.FRONTEND_URL,
        }
        
        message = render_to_string('emails/password_reset_email.html', context)
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message,
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f'Failed to send password reset email: {str(e)}', exc_info=True)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not all([uid, token, new_password]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Decode the uid to get the user
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            # Verify the token
            if not default_token_generator.check_token(user, token):
                return Response(
                    {'error': 'Invalid or expired token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set the new password
            user.set_password(new_password)
            user.save()
            
            return Response({
                'message': 'Password has been reset successfully.'
            })
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid user or token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        obj, created = UserProfile.objects.get_or_create(user=self.request.user)
        return obj
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        profile = self.get_object()
        if request.method == 'PUT':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        if not name:
            return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        api_key = APIKey.objects.create(
            user=request.user,
            name=name
        )
        
        AuditLog.objects.create(
            user=request.user,
            action='create_api_key',
            ip_address=self.get_client_ip(request),
            details={'api_key_id': str(api_key.id), 'name': name}
        )
        
        serializer = self.get_serializer(api_key)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail='pk', methods=['post'])
    def revoke(self, request, pk=None):
        api_key = self.get_object()
        api_key.status = 'revoked'
        api_key.save()
        
        AuditLog.objects.create(
            user=request.user,
            action='revoke_api_key',
            ip_address=self.get_client_ip(request),
            details={'api_key_id': str(api_key.id)}
        )
        
        return Response({'status': 'API key revoked'})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PaymentProviderViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentProviderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentProvider.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        provider = request.data.get('provider')
        public_key = request.data.get('public_key')
        secret_key = request.data.get('secret_key')
        
        existing = PaymentProvider.objects.filter(
            user=request.user,
            provider=provider
        ).first()
        
        if existing:
            existing.public_key = public_key
            existing.secret_key = secret_key
            existing.save()
            serializer = self.get_serializer(existing)
            return Response(serializer.data)
        
        payment_provider = PaymentProvider.objects.create(
            user=request.user,
            provider=provider,
            public_key=public_key,
            secret_key=secret_key
        )
        
        AuditLog.objects.create(
            user=request.user,
            action='update_payment_provider',
            ip_address=self.get_client_ip(request),
            details={'provider': provider}
        )
        
        serializer = self.get_serializer(payment_provider)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'provider', 'currency']
    ordering_fields = ['created_at', 'amount']
    search_fields = ['reference', 'customer_email']
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related('api_key')
    
    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        """Initiate payment with idempotency key to prevent double charging"""
        api_key_id = request.data.get('api_key_id')
        provider = request.data.get('provider')
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'NGN')
        customer_email = request.data.get('customer_email')
        description = request.data.get('description', '')
        idempotency_key = request.data.get('idempotency_key')
        use_tokenization = request.data.get('use_tokenization', True)
        save_card = request.data.get('save_card', False)
        
        if idempotency_key:
            existing_transaction = Transaction.objects.filter(
                idempotency_key=idempotency_key,
                user=request.user
            ).first()
            
            if existing_transaction:
                # Return existing transaction instead of creating duplicate
                serializer = self.get_serializer(existing_transaction)
                return Response(
                    {'data': serializer.data, 'message': 'Using existing transaction'},
                    status=status.HTTP_200_OK
                )
        
        api_key_obj = get_object_or_404(APIKey, id=api_key_id, user=request.user, status='active')
        payment_provider = get_object_or_404(PaymentProvider, provider=provider, user=request.user)
        
        transaction = Transaction.objects.create(
            user=request.user,
            api_key=api_key_obj,
            provider=provider,
            amount=Decimal(str(amount)),
            currency=currency,
            customer_email=customer_email,
            description=description,
            reference=f"{provider}_{timezone.now().timestamp()}",
            idempotency_key=idempotency_key,
            status='pending',
        )
        
        transaction.calculate_fee()
        transaction.save()
        
        if provider == 'stripe' and use_tokenization:
            try:
                payment_service = PaymentService()
                result = payment_service.create_tokenized_payment(
                    transaction=transaction,
                    customer_email=customer_email,
                    amount=amount,
                    currency=currency,
                    save_card=save_card
                )
                
                if result.get('success'):
                    transaction.stripe_payment_method_id = result.get('payment_method_id')
                    transaction.provider_response = result
                    transaction.save()
                    
                    # Queue webhook processing as async task
                    process_transaction_webhook.delay(
                        transaction_id=str(transaction.id),
                        idempotency_key=idempotency_key
                    )
                else:
                    transaction.status = 'failed'
                    transaction.provider_response = result
                    transaction.save()
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                transaction.status = 'failed'
                transaction.provider_response = {'error': str(e)}
                transaction.save()
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail='pk', methods=['get'])
    def verify_payment(self, request, pk=None):
        """Verify payment status"""
        transaction = self.get_object()
        
        if transaction.provider == 'paystack':
            response = self._verify_paystack(transaction)
        elif transaction.provider == 'flutterwave':
            response = self._verify_flutterwave(transaction)
        elif transaction.provider == 'stripe':
            response = self._verify_stripe(transaction)
        else:
            response = {'status': 'unsupported'}
        
        return Response(response)
    
    def _verify_paystack(self, transaction):
        from django.conf import settings
        headers = {'Authorization': f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        url = f"https://api.paystack.co/transaction/verify/{transaction.reference}"
        response = requests.get(url, headers=headers)
        return response.json()
    
    def _verify_flutterwave(self, transaction):
        from django.conf import settings
        headers = {'Authorization': f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
        url = f"https://api.flutterwave.com/v3/transactions/{transaction.reference}/verify"
        response = requests.get(url, headers=headers)
        return response.json()
    
    def _verify_stripe(self, transaction):
        import stripe
        from django.conf import settings
        stripe.api_key = settings.STRIPE_API_KEY
        
        try:
            payment_intent = stripe.PaymentIntent.retrieve(transaction.reference)
            return {
                'status': payment_intent.status,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency,
            }
        except Exception as e:
            return {'error': str(e)}


class WebhookViewSet(viewsets.ModelViewSet):
    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Webhook.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        webhook = Webhook.objects.create(
            user=request.user,
            url=request.data.get('url'),
            event_types=request.data.get('event_types', [])
        )
        
        AuditLog.objects.create(
            user=request.user,
            action='create_webhook',
            ip_address=self.get_client_ip(request),
            details={'webhook_id': str(webhook.id)}
        )
        
        serializer = self.get_serializer(webhook)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        obj, created = Subscription.objects.get_or_create(
            user=self.request.user,
            defaults={
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timedelta(days=30),
                'renewal_date': timezone.now() + timedelta(days=30),
            }
        )
        return obj
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        subscription = self.get_object()
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)


class KYCViewSet(viewsets.ViewSet):
    """KYC verification endpoints"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def verify_bvn(self, request):
        bvn = request.data.get('bvn')
        provider = request.data.get('provider', 'mono')
        
        if not bvn:
            return Response({'error': 'BVN is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = KYCService.verify_bvn(request.user, bvn, provider)
            return Response(result)
        except KYCVerificationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def verify_account(self, request):
        account_number = request.data.get('account_number')
        bank_code = request.data.get('bank_code')
        provider = request.data.get('provider', 'mono')
        
        if not account_number or not bank_code:
            return Response({'error': 'Account number and bank code required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = KYCService.verify_account(request.user, account_number, bank_code, provider)
            return Response(result)
        except KYCVerificationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def verification_status(self, request):
        verifications = KYCVerification.objects.filter(user=request.user)
        serializer = KYCVerificationSerializer(verifications, many=True)
        return Response(serializer.data)


class AnalyticsViewSet(viewsets.ViewSet):
    """Analytics endpoints"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def transactions(self, request):
        days = int(request.query_params.get('days', 30))
        analytics = AnalyticsService.get_transaction_analytics(request.user, days)
        return Response(analytics)
    
    @action(detail=False, methods=['get'])
    def usage(self, request):
        days = int(request.query_params.get('days', 30))
        analytics = AnalyticsService.get_api_usage_analytics(request.user, days)
        return Response(analytics)
    
    @action(detail=False, methods=['get'])
    def revenue(self, request):
        days = int(request.query_params.get('days', 30))
        analytics = AnalyticsService.get_revenue_analytics(request.user, days)
        return Response(analytics)


class BillingViewSet(viewsets.ViewSet):
    """Billing and invoicing endpoints"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def invoices(self, request):
        invoices = Invoice.objects.filter(user=request.user)
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def usage_metrics(self, request):
        metrics = UsageMetric.objects.filter(user=request.user)
        serializer = UsageMetricSerializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def generate_invoice(self, request):
        billing_period_start = request.data.get('period_start')
        billing_period_end = request.data.get('period_end')
        
        if not billing_period_start or not billing_period_end:
            return Response({'error': 'Period start and end required'}, status=status.HTTP_400_BAD_REQUEST)
        
        invoice = BillingService.generate_invoice(request.user, billing_period_start, billing_period_end)
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Audit logs - read only"""
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        return AuditLog.objects.filter(user=self.request.user)
