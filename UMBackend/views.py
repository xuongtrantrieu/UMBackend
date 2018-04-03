from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.contrib.auth import authenticate, login, logout, get_user
from rest_framework.authtoken.models import Token
from rest_framework_jwt.settings import api_settings

from addons.core.users.serializers import UserSerializer
from utils.shortcuts import expire_token
from lib.logger import Logger


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


@api_view(['GET', ])
def _api_root():
    return Response('Welcome to my API.')


class CurrentUser(APIView):
    @staticmethod
    def get(request):
        user = get_user(request)
        if user.is_anonymous:
            context = {
                'message': 'ANONYMOUS USER.',
                'status': 404,
            }
            return Response(context, status=context['status'])
        context = {
            'message': 'OK',
            'status': 200,
            'data': UserSerializer(user).data
        }
        return Response(context, status=context['status'])


class Login(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)

    @staticmethod
    def post(request):
        data = request.data
        email = data.get('email', '').lower()

        if not email:
            context = {
                'status': 400,
                'message': 'USER NOT FOUND.'
            }
            return Response(context, status=context['status'])

        # Check if user has logged in or not
        user = get_user(request)
        if not user.is_anonymous:
            context = {
                'message': 'USER ALREADY LOGGED IN.',
                'status': 400
            }
            return Response(context, status=context['status'])

        password = data.get('password', '')
        user = authenticate(request, email=email, password=password)
        if not user:
            Logger().info(
                '{} user {}'.format('LOGIN', data)
            )
            context = {
                'message': 'INCORRECT LOGIN INFORMATION.',
                'status': 400,
            }
            return Response(context, status=context['status'])

        # Skipped checking if user is active or not, user is active by default so I make this simpler

        login(request, user)
        previous_token = Token.objects.get(user=get_user(request))
        expired = expire_token(previous_token)
        if expired:
            previous_token.delete()

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.user_token = token
        user.save()

        context = {
            'message': 'OK',
            'status': 200,
            'data': UserSerializer(user).data
        }

        return Response(context, status=context['status'])


class Logout(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)

    @staticmethod
    def get(request):
        user = get_user(request)
        if user.is_anonymous:
            context = {
                'message': 'ANONYMOUS USER.',
                'status': 404
            }
            return Response(context, status=context['status'])

        token = Token.objects.get(user=user)
        expire_token(token)
        user.user_token = ''
        user.save()
        logout(request=request)

        context = {
            'message': "TOKEN DELETED.",
            'status': 200,
            'data': UserSerializer(user).data
        }
        return Response(context, context['status'])
