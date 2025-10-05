"""
User models for Apatye project.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel


class UserManager(BaseUserManager):
    """
    Custom user manager for mobile-based authentication.
    """
    def create_user(self, mobile, password=None, **extra_fields):
        """Create and save a regular user with the given mobile and password."""
        if not mobile:
            raise ValueError(_('The Mobile field must be set'))
        
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        """Create and save a superuser with the given mobile and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(mobile, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom user model with mobile-based authentication.
    """
    class UserType(models.TextChoices):
        CUSTOMER = 'customer', _('Customer')
        VENDOR = 'vendor', _('Vendor')
        ADMIN = 'admin', _('Admin')

    mobile = models.CharField(_('Mobile number'), max_length=11, unique=True, db_index=True)
    email = models.EmailField(_('Email address'), blank=True, null=True)
    first_name = models.CharField(_('First name'), max_length=150, blank=True)
    last_name = models.CharField(_('Last name'), max_length=150, blank=True)
    user_type = models.CharField(_('User type'), max_length=20, choices=UserType.choices, default=UserType.CUSTOMER)
    
    is_active = models.BooleanField(_('Active'), default=True)
    is_staff = models.BooleanField(_('Staff status'), default=False)
    is_verified = models.BooleanField(_('Mobile verified'), default=False)
    
    objects = UserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'users'

    def __str__(self):
        return self.mobile

    def get_full_name(self):
        """Return the user's full name."""
        return f'{self.first_name} {self.last_name}'.strip() or self.mobile


class OTPCode(TimeStampedModel):
    """
    OTP codes for mobile verification.
    """
    mobile = models.CharField(_('Mobile number'), max_length=11, db_index=True)
    code = models.CharField(_('OTP Code'), max_length=6)
    is_used = models.BooleanField(_('Is used'), default=False)
    expires_at = models.DateTimeField(_('Expires at'))

    class Meta:
        verbose_name = _('OTP Code')
        verbose_name_plural = _('OTP Codes')
        db_table = 'user_otp_codes'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.mobile} - {self.code}'

    def is_valid(self):
        """Check if OTP is still valid."""
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()
