"""
Alternative implementation of Django's authentication User model, which allows to authenticate
against the email field in addition to the username fields.
This alternative implementation is activated by setting ``AUTH_USER_MODEL = 'shop.User'`` in
settings.py, otherwise the default Django or another customized implementation will be used.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):

    def _create_user(self, username, email_phone, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        username = self.model.normalize_username(username)
        user = self.model(username=username, email_phone=email_phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email_phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email_phone, password, **extra_fields)

    def create_superuser(self, username, email_phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email_phone, password, **extra_fields)

    def get_by_natural_key(self, email_phone):
        if is_phone(email_phone):
            try:
                return self.get(phone=email_phone)
            except:
                pass
        if is_email(email_phone):
            try:
                return self.get(email=email_phone)
            except:
                pass
        return self.get(is_active=True, email_phone=email_phone)


@python_2_unicode_compatible
class User(AbstractUser):
    """
    Alternative implementation of Django's User model allowing to authenticate against the email
    field in addition to the username field, which remains the primary unique identifier. The
    email field is only used in addition. For users marked as active, their email address must
    be unique. Guests can reuse their email address as often they want.
    """
    phone = PhoneNumberField(
        _('Phone number'),
        max_length=150,
        default=None,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Required. 150 characters or fewer. Digits and + only.'),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), blank=True, unique=True, default=None, null=True)
    email_phone = models.CharField(unique=True, max_length=150, blank=True, default=None, null=True,
                                   error_messages={'unique': _("A user with that username already exists."), },
                                   )
    objects = UserManager()

    USERNAME_FIELD = 'email_phone'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'auth_user'
        verbose_name = _("Customer phone number")
        verbose_name_plural = _("Customers phone number")
        swappable = 'AUTH_USER_MODEL'

    def get_username(self):
        if self.email_phone is not None:
            return self.email_phone
        elif self.phone is not None:
            return str(self.phone)
        else:
            return self.email

    def __str__(self):
        if self.is_staff or self.is_superuser:
            return self.username
        elif self.phone is not None:
            return str(self.phone)
        return self.email_phone or '<anonymous>'

    def get_full_name(self):
        full_name = super(User, self).get_full_name()
        if full_name:
            return full_name
        return self.get_short_name()

    def get_short_name(self):
        short_name = super(User, self).get_short_name()
        if short_name:
            return short_name
        return self.email_phone

    def validate_unique(self, exclude=None):
        """
        Since the email address is used as the primary identifier, we must ensure that it is
        unique. However, since this constraint only applies to active users, it can't be done
        through a field declaration via a database UNIQUE index.

        Inactive users can't login anyway, so we don't need a unique constraint for them.
        """
        super(User, self).validate_unique(exclude)
        if self.email_phone and get_user_model().objects.exclude(id=self.id).filter(is_active=True,
                                                                                    email_phone__exact=self.email_phone).exists():
            msg = _("A customer with the e-mail address or phone number ‘{email_phone}’ already exists.")
            raise ValidationError({'email_phone': msg.format(email_phone=self.email_phone)})


    def save(self, *args, **kwargs):
        if is_phone(self.email_phone):
            self.phone = self.email_phone
            if not hasattr(self, 'email') or not is_email(self.email):
                self.email = None
        elif is_email(self.email_phone):
            self.email = self.email_phone
        super().save(*args, **kwargs)

def is_phone(phone):
    try:
        if '+' in phone:
            return True
        else:
            return False
    except:
        return False


def is_email(email):
    try:
        if '@' in email:
            return True
        else:
            return False
    except:
        return False
