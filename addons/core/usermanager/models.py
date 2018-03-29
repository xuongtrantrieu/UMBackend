from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    A customer user manager to deal with emails as unique identifiers for auth instead of usernames.
    """

    @classmethod
    def _create_user(cls, email, password, ** kwargs):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The email must be set')
        email = cls.normalize_email(email)
        user = cls.model(email=email, ** kwargs)
        user.set_password(password)
        user.save()
        return user

    @classmethod
    def create_superuser(cls, email, password, ** kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **kwargs)
