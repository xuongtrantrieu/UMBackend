from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from addons.core.usermanager.models import UserManager

from rest_framework_jwt.settings import api_settings

NAME_MAX_LENGTH = 100

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    first_name = models.CharField(max_length=NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=NAME_MAX_LENGTH)
    is_superuser = models.BooleanField(
        default=False,
        help_text='This is a superuser, I think.'
    )
    is_staff = models.BooleanField(
        'staff status',
        default = True,
        help_text='Designates whether the user can log into this site.'
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Designates whether this user should be treated as active.\nUnselect this instead of deleting accounts.'
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

    def token(self):
        self.user_token = self.generate_token()
        return self.user_token

    def generate_token(self):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(self)
        token = jwt_encode_handler(payload)

        return token
