"""
WSGI config for UMBackend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
from os import sys
sys.path.append('~/Projects/UserManagement/UMBackend')
sys.path.append('~/Projects/UserManagement/UMBackend/UMBackend')
from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UMBackend.settings")

application = get_wsgi_application()
