from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from addons.core.usermanager.models import UserManager
# from django.utils.translation import ugettext_lazy as _

NAME_MAX_LENGTH = 100

class User(AbstractBaseUser):
    email = models.EmailField(unique=True, null=True)
    first_name = models.CharField(max_length=NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=NAME_MAX_LENGTH)
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
    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return'{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name
