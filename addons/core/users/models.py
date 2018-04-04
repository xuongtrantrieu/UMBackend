from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from addons.core.usermanager.models import UserManager

NAME_MAX_LENGTH = 100


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    first_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, default='')
    last_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, default='')
    is_superuser = models.BooleanField(
        default=False,
        help_text='This is a superuser, I think.'
    )
    is_staff = models.BooleanField(
        'staff status',
        default=True,
        help_text='Designates whether the user can log into this site.'
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Designates whether this user should be treated as active.\n'
                  'Unselect this instead of deleting accounts. '
    )
    user_token = models.TextField(max_length=200, null=True, blank=True)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return'{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def update(self, **kwargs):
        email = kwargs.get('email', self.email)
        first_name = kwargs.get('first_name', self.first_name)
        last_name = kwargs.get('last_name', self.last_name)
        is_superuser = kwargs.get('is_superuser', self.is_superuser)
        is_staff = kwargs.get('is_staff', self.is_staff)
        is_active = kwargs.get('is_active', self.is_active)
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.is_superuser = is_superuser
        self.is_staff = is_staff
        self.is_active = is_active
        self.save()

