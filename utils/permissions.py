import re
from rest_framework import permissions

from utils.shortcuts import get_or_none

from rest_framework.views import exception_handler
from utils.code import code
from rest_framework import authentication
from django.conf import settings
import os
import time
import datetime
from django.contrib.auth import get_user

PATTERN = r'(.*)-(.*)'
BASE_DIR = settings.BASE_DIR


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the user.
        return obj.owner == request.user


class UserIsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the user.
        return obj.user == request.user


class UserIsOwnerOrRead(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the user.
        return obj == request.user


class RequestUserIsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to check for friend request owner
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the user.
        return obj.fromuser == request.user


class UserIsOwnerOrDenie(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsNotAuthenticated(permissions.IsAuthenticated):
    """
    Restrict access only to unauthenticated users.
    """
    def has_permission(self, request, view, obj=None):
        if request.user and request.user.is_authenticated:
            return False
        else:
            return True


class CusIsAuthenticated(permissions.IsAuthenticated):
    """
        Restrict access only to unauthenticated users.
    """

    authentication_header_prefix = 'token'

    def has_permission(self, request, view, obj=None):
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if auth_header:
            prefix = auth_header[0].decode('utf-8')
            token = auth_header[1].decode('utf-8')

            TOKEN_FILE = "token_blacklist"
            time_path = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d')
            file_token = TOKEN_FILE + '_' + time_path + '.txt'
            PATH_TOKEN_BLACKLIST = os.path.join(BASE_DIR, "data", "token_blacklist", file_token)

        user = get_user(request)
        # return Response(user.email)
        if user and user.is_authenticated:
            try:
                with open(PATH_TOKEN_BLACKLIST, 'r') as f:
                    raw_data = f.read()
                data = raw_data.split()
            except IOError:
                data = []

            flag = True
            if not data:
                with open(PATH_TOKEN_BLACKLIST, 'a') as f:
                    f.write('%s\n' % (token))
                flag = True
            else:
                for black_token in data:
                    if black_token == token:
                        flag = False
                        break
                if flag:
                    with open(PATH_TOKEN_BLACKLIST, 'a') as f:
                        f.write('%s\n' % (token))
                        flag = True

            return flag
        else:
            return False


class CusCheckIsAuthenticated(permissions.IsAuthenticated):
    """
        Restrict access only to unauthenticated users.
    """

    authentication_header_prefix = 'token'

    def has_permission(self, request, view, obj=None):
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if auth_header:
            prefix = auth_header[0].decode('utf-8')
            token = auth_header[1].decode('utf-8')

            TOKEN_FILE = "token_blacklist"
            time_path = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d')
            file_token = TOKEN_FILE + '_' + time_path + '.txt'

            PATH_TOKEN_BLACKLIST = os.path.join(BASE_DIR, "data", "token_blacklist", file_token)

            try:
                with open(PATH_TOKEN_BLACKLIST, 'r') as f:
                    raw_data = f.read()
                data = raw_data.split()
            except IOError:
                data = []

        if request.user and request.user.is_authenticated:
            flag = True
            for black_token in data:
                if black_token == token:
                    flag = False
            return flag
        else:
            return False


def is_password(request):
    if not request.user.check_password(request.DATA['password']):
            return False
    return True


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status'] = response.status_code
        if response.data['detail'] == "Invalid token.":
            response.data["code"] = list(code.keys())[list(code.values()).index('Invalid token.')]
        elif response.data['detail'] == "Authentication credentials were not provided.":
            response.data["code"] = list(code.keys())[list(code.values()).index('Authentication credentials were not provided.')]
        elif response.data['detail'] == "Paginate out of range":
            response.data["code"] = list(code.keys())[list(code.values()).index('Paginate out of range')]
    try:
        response.data['message'] = response.data.pop('detail')
    except Exception as e:
        print(e)
        pass

    return response
