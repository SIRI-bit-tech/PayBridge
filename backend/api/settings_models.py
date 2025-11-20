"""
Settings Models for PayBridge
Handles business profile and payment provider configurations
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from cryptography.fernet import Fernet
from django.conf import settings
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


def get_encryption_key():
    """Get encryption key from settings"""
    key = getattr(settings, 'ENCRYPTION_KEY', None)
    if not key:
        # Generate a key if not set (for development only)
        key = Fernet.generate_key()
        logger.warning("No ENCRYPTION_KEY set in settings, using generated key")
    if isinstance(key, str):
        key = key.encode()
    return key


class EncryptedField:
    """Helper class for encrypting/decrypting sensitive fields"""
    
    @staticmethod
    def encrypt(value: str) -> str:
        """Encrypt a string value"""
        if not value:
            return value
        try:
            f = Fernet(get_encryption_key())
            return f.encrypt(value.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            return value
    
    @staticmethod
    def decrypt(value: str) -> str:
        """Decrypt a string value"""
        if not value:
            return value
        try:
            f = Fernet(get_encryption_key())
            return f.decrypt(value.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            return value


class BusinessProfile(models.Model):
    """
    Extended business profile settings
    Separate from UserProfile for better organization
    """
    BUSINESS_TYPE_CHOICES = (
        ('sole_proprietorship', 'Sole Proprietorship'),
        ('partnership', 'Partnership'),
        ('llc', 'Limited Liability Company'),
        ('corporation', 'Corporation'),
        ('nonprofit', 'Non-Profit'),
        ('other', 'Other'),
    )
    
    COUNTRY_CHOICES = (
        ('NG', 'Nigeria'),
        ('GH', 'Ghana'),
        ('KE', 'Kenya'),
        ('UG', 'Uganda'),
        ('TZ', 'Tanzania'),
        ('ET', 'Ethiopia'),
        ('ZA', 'South Africa'),
        ('US', 'United States'),
        ('GB', 'United Kingdom'),
        ('CA', 'Canada'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business_profile')
    company_name = models.CharField(max_length=255)
    business_phone = models.CharField(max_length=20, blank=True)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPE_CHOICES, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default='NG')
    
    # Additional fields
    business_email = models.EmailField(blank=True)
    business_address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True, validators=[URLValidator()])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'business_profiles'
    
    def __str__(self):
        return f"{self.company_name} ({self.user.email})"


class PaymentProviderConfig(models.Model):
    """
    Enhanced payment provider configuration with encryption
    Replaces the basic PaymentProvider model
    """
    PROVIDER_CHOICES = (
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('stripe', 'Stripe'),
    )
    
    MODE_CHOICES = (
        ('test', 'Test Mode'),
        ('live', 'Live Mode'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_configs')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    
    # Encrypted credentials
    public_key_encrypted = models.TextField()
    secret_key_encrypted = models.TextField()
    
    # Mode and status
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='test')
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)  # Primary provider for payments
    
    # Validation
    credentials_validated = models.BooleanField(default=False)
    last_validated_at = models.DateTimeField(null=True, blank=True)
    validation_error = models.TextField(blank=True)
    
    # Webhook configuration
    webhook_url = models.URLField(blank=True)
    webhook_secret = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_provider_configs'
        unique_together = ('user', 'provider', 'mode')
        indexes = [
            models.Index(fields=['user', 'is_active', 'is_primary']),
        ]
    
    def set_public_key(self, value: str):
        """Encrypt and set public key"""
        self.public_key_encrypted = EncryptedField.encrypt(value)
    
    def get_public_key(self) -> str:
        """Decrypt and get public key"""
        return EncryptedField.decrypt(self.public_key_encrypted)
    
    def set_secret_key(self, value: str):
        """Encrypt and set secret key"""
        self.secret_key_encrypted = EncryptedField.encrypt(value)
    
    def get_secret_key(self) -> str:
        """Decrypt and get secret key"""
        return EncryptedField.decrypt(self.secret_key_encrypted)
    
    def get_masked_public_key(self) -> str:
        """Return masked version of public key"""
        try:
            key = self.get_public_key()
            if len(key) > 12:
                return f"{key[:8]}****{key[-4:]}"
            return "****"
        except:
            return "****"
    
    def get_masked_secret_key(self) -> str:
        """Return masked version of secret key"""
        try:
            key = self.get_secret_key()
            if len(key) > 12:
                return f"{key[:8]}****{key[-4:]}"
            return "****"
        except:
            return "****"
    
    def __str__(self):
        return f"{self.user.email} - {self.provider} ({self.mode})"
