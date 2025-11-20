"""
Settings API Views with Real-time Updates
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction

from .settings_models import BusinessProfile, PaymentProviderConfig
from .settings_serializers import (
    BusinessProfileSerializer, PaymentProviderConfigSerializer,
    UserProfileSerializer
)
from .models import UserProfile, AuditLog
from .provider_validation_service import ProviderValidationService
from .redis_pubsub import publish_event
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


class BusinessProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing business profile settings
    Includes real-time updates via Socket.IO and Redis
    """
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BusinessProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create business profile for current user"""
        profile, created = BusinessProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'company_name': self.request.user.profile.company_name or '',
                'country': self.request.user.profile.country,
                'business_phone': self.request.user.profile.phone_number or '',
                'business_type': self.request.user.profile.business_type or '',
            }
        )
        return profile
    
    def list(self, request, *args, **kwargs):
        """Return current user's business profile"""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update business profile with real-time sync"""
        profile = self.get_object()
        old_data = BusinessProfileSerializer(profile).data
        
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Save the profile
            serializer.save()
            
            # Also update UserProfile for backward compatibility
            user_profile = request.user.profile
            if 'company_name' in request.data:
                user_profile.company_name = request.data['company_name']
            if 'country' in request.data:
                user_profile.country = request.data['country']
            if 'business_phone' in request.data:
                user_profile.phone_number = request.data['business_phone']
            if 'business_type' in request.data:
                user_profile.business_type = request.data['business_type']
            user_profile.save()
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='settings.profile_updated',
                resource_type='business_profile',
                resource_id=str(profile.id),
                details={
                    'old_values': old_data,
                    'new_values': serializer.data,
                    'ip_address': self._get_client_ip(request)
                }
            )
        
        # Publish real-time update via Redis
        publish_event('settings_updates', {
            'type': 'profile_updated',
            'user_id': request.user.id,
            'data': serializer.data
        })
        
        return Response({
            'message': 'Profile updated successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's profile (alias for list)"""
        return self.list(request)
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PaymentProviderConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment provider configurations
    Includes credential validation and real-time updates
    """
    serializer_class = PaymentProviderConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentProviderConfig.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create provider config with validation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract credentials for validation
        public_key = request.data.get('public_key', '')
        secret_key = request.data.get('secret_key', '')
        provider = request.data.get('provider')
        mode = request.data.get('mode', 'test')
        
        # Validate credentials
        is_valid, error_message = ProviderValidationService.validate_provider(
            provider, public_key, secret_key, mode
        )
        
        with transaction.atomic():
            # Save the config
            instance = serializer.save(
                user=request.user,
                credentials_validated=is_valid,
                last_validated_at=timezone.now() if is_valid else None,
                validation_error=error_message if not is_valid else ''
            )
            
            # If this is the first provider, make it primary
            if not PaymentProviderConfig.objects.filter(
                user=request.user, is_primary=True
            ).exclude(id=instance.id).exists():
                instance.is_primary = True
                instance.save()
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='settings.provider_added',
                resource_type='payment_provider',
                resource_id=str(instance.id),
                details={
                    'provider': provider,
                    'mode': mode,
                    'validated': is_valid,
                    'ip_address': self._get_client_ip(request)
                }
            )
        
        # Publish real-time update via Redis
        response_data = PaymentProviderConfigSerializer(instance).data
        publish_event('provider_updates', {
            'type': 'provider_added',
            'user_id': request.user.id,
            'data': response_data
        })
        
        return Response({
            'message': 'Provider added successfully' if is_valid else 'Provider added but validation failed',
            'data': response_data,
            'validated': is_valid,
            'validation_error': error_message if not is_valid else None
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update provider config with validation"""
        instance = self.get_object()
        old_mode = instance.mode
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # If credentials are being updated, validate them
        public_key = request.data.get('public_key')
        secret_key = request.data.get('secret_key')
        
        is_valid = instance.credentials_validated
        error_message = instance.validation_error
        
        if public_key or secret_key:
            # Get current keys if not provided
            if not public_key:
                public_key = instance.get_public_key()
            if not secret_key:
                secret_key = instance.get_secret_key()
            
            # Validate
            is_valid, error_message = ProviderValidationService.validate_provider(
                instance.provider, public_key, secret_key, 
                request.data.get('mode', instance.mode)
            )
        
        with transaction.atomic():
            # Save the config
            instance = serializer.save(
                credentials_validated=is_valid,
                last_validated_at=timezone.now() if is_valid else instance.last_validated_at,
                validation_error=error_message if not is_valid else ''
            )
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='settings.provider_updated',
                resource_type='payment_provider',
                resource_id=str(instance.id),
                details={
                    'provider': instance.provider,
                    'mode': instance.mode,
                    'mode_changed': old_mode != instance.mode,
                    'validated': is_valid,
                    'ip_address': self._get_client_ip(request)
                }
            )
        
        # Publish real-time update via Redis
        response_data = PaymentProviderConfigSerializer(instance).data
        publish_event('provider_updates', {
            'type': 'provider_updated',
            'user_id': request.user.id,
            'data': response_data,
            'mode_changed': old_mode != instance.mode
        })
        
        return Response({
            'message': 'Provider updated successfully',
            'data': response_data,
            'validated': is_valid,
            'validation_error': error_message if not is_valid else None
        })
    
    def destroy(self, request, *args, **kwargs):
        """Delete provider config"""
        instance = self.get_object()
        provider_name = instance.provider
        
        with transaction.atomic():
            # Create audit log before deletion
            AuditLog.objects.create(
                user=request.user,
                action='settings.provider_deleted',
                resource_type='payment_provider',
                resource_id=str(instance.id),
                details={
                    'provider': provider_name,
                    'mode': instance.mode,
                    'ip_address': self._get_client_ip(request)
                }
            )
            
            instance.delete()
        
        # Publish real-time update via Redis
        publish_event('provider_updates', {
            'type': 'provider_deleted',
            'user_id': request.user.id,
            'data': {'id': str(instance.id), 'provider': provider_name}
        })
        
        return Response({
            'message': 'Provider deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Manually validate provider credentials"""
        instance = self.get_object()
        
        # Get decrypted keys
        public_key = instance.get_public_key()
        secret_key = instance.get_secret_key()
        
        # Validate
        is_valid, error_message = ProviderValidationService.validate_provider(
            instance.provider, public_key, secret_key, instance.mode
        )
        
        # Update validation status
        instance.credentials_validated = is_valid
        instance.last_validated_at = timezone.now() if is_valid else None
        instance.validation_error = error_message if not is_valid else ''
        instance.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='settings.provider_validated',
            resource_type='payment_provider',
            resource_id=str(instance.id),
            details={
                'provider': instance.provider,
                'validated': is_valid,
                'error': error_message if not is_valid else None,
                'ip_address': self._get_client_ip(request)
            }
        )
        
        return Response({
            'validated': is_valid,
            'error': error_message if not is_valid else None,
            'last_validated_at': instance.last_validated_at
        })
    
    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        """Set this provider as primary"""
        instance = self.get_object()
        
        with transaction.atomic():
            # Remove primary flag from other providers
            PaymentProviderConfig.objects.filter(
                user=request.user, is_primary=True
            ).update(is_primary=False)
            
            # Set this as primary
            instance.is_primary = True
            instance.save()
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='settings.provider_set_primary',
                resource_type='payment_provider',
                resource_id=str(instance.id),
                details={
                    'provider': instance.provider,
                    'mode': instance.mode,
                    'ip_address': self._get_client_ip(request)
                }
            )
        
        # Publish real-time update via Redis
        publish_event('provider_updates', {
            'type': 'provider_primary_changed',
            'user_id': request.user.id,
            'data': PaymentProviderConfigSerializer(instance).data
        })
        
        return Response({
            'message': f'{instance.provider} set as primary provider',
            'data': PaymentProviderConfigSerializer(instance).data
        })
    
    @action(detail=True, methods=['post'])
    def toggle_mode(self, request, pk=None):
        """Toggle between test and live mode"""
        instance = self.get_object()
        old_mode = instance.mode
        new_mode = 'live' if old_mode == 'test' else 'test'
        
        with transaction.atomic():
            instance.mode = new_mode
            instance.save()
            
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='settings.provider_mode_toggled',
                resource_type='payment_provider',
                resource_id=str(instance.id),
                details={
                    'provider': instance.provider,
                    'old_mode': old_mode,
                    'new_mode': new_mode,
                    'ip_address': self._get_client_ip(request)
                }
            )
        
        # Publish real-time update via Redis
        response_data = PaymentProviderConfigSerializer(instance).data
        publish_event('provider_updates', {
            'type': 'provider_mode_changed',
            'user_id': request.user.id,
            'data': response_data,
            'old_mode': old_mode,
            'new_mode': new_mode
        })
        
        return Response({
            'message': f'Switched to {new_mode} mode',
            'data': response_data
        })
    
    @action(detail=False, methods=['get'])
    def primary(self, request):
        """Get primary provider"""
        provider = PaymentProviderConfig.objects.filter(
            user=request.user, is_primary=True, is_active=True
        ).first()
        
        if not provider:
            return Response({
                'message': 'No primary provider configured'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(provider)
        return Response(serializer.data)
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
