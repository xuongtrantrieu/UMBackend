from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import Group


class UserManager(BaseUserManager):
    """
    A customer user manager to deal with emails as unique identifiers for auth instead of usernames.
    """

    def _create_user(self, email, password, **kwargs):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self._create_user(email, password, ** kwargs)

        try:
            superusers = Group.objects.get(name__iexact='superusers')
        except Group.DoesNotExist:
            superusers = Group.objects.create(name='Superusers')
        user.groups.add(superusers)
        user.save()
        return user
