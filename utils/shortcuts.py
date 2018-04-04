from django.utils import timezone
from datetime import timedelta
from UMBackend import settings
from rest_framework.response import Response


def get_or_none(model, *args, **kwargs):
    """
        get a model or return None if not found
        pass in a model with filters
    """
    try:
        return model.objects.get(*args, **kwargs)
    except (model.DoesNotExist, ValueError, Exception):
        return None


def expire_token(token):
    min_age = timezone.now() - timedelta(
        seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS)
    expired = token.created < min_age
    return expired


def make_response(context):
    return Response(context, status=context.get('status', 200))
