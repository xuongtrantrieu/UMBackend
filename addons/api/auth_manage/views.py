from rest_framework.views import APIView
from addons.core.users.models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from lib.logger import Logger
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from utils.shortcuts import make_response, expire_token
from django.contrib.auth import get_user, authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework_jwt.settings import api_settings
from utils.permissions import CusCheckIsAuthenticated


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class Register(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        data = request.data
        Logger().info(
            '{} user {}'.format('POST', data)
        )
        is_valid = self.serializer_class(data=data).is_valid()

        if not is_valid:
            email = data.get('email', '')
            if User.objects.filter(email=email).first():
                context = {
                    'status': 400,
                    'message': 'EMAIL IS ALREADY IN USED.'
                }
                return make_response(context)

        user, _ = User.objects.update_or_create(
            email=data.get('email', ''),
            password=make_password(data.get('password', '')),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )

        user_serialized = self.serializer_class(user, many=False).data
        context = {
            'data': user_serialized,
            'message': 'OK',
            'status': 200
        }

        return make_response(context)


class EditCurrentUser(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (CusCheckIsAuthenticated,)

    def put(self, request):
        data = request.data
        user = get_user(request)

        Logger().info(
            '{} user {}'.format('PUT', data)
        )

        if user.is_anonymous:
            context = {
                'message': 'ANONYMOUS USER.',
                'status': 400
            }
            return make_response(context)

        # is_valid = UserSerializer(data=data).is_valid()
        #
        # if not is_valid:
        #     context = {
        #         'message': 'INVALID INPUT DATA.',
        #         'status': 400,
        #         'data': data
        #     }
        #     return make_response(context)

        email = data.get('email', '')
        if user.email != email and len(User.objects.filter(email=email)) == 1:
            context = {
                'message': 'THIS EMAIL IS ALREADY IN USED.',
                'status': 400,
                'data': data
            }
            return make_response(context)
        # context = {
        #     'message': 'DEBUG.',
        #     'status': 400,
        #     'email used times': len(User.objects.filter(email=email)),
        #     'data': data
        # }
        # return make_response(context)

        password = make_password(data.get('password', user.password))
        first_name = data.get('first_name', user.first_name)
        last_name = data.get('last_name', user.last_name)
        user.update(email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name)

        user_serialized = UserSerializer(user)

        context = {
            'message': 'OK',
            'status': 200,
            'data': user_serialized.data
        }
        return make_response(context)


class UserList(APIView):
    def get(self, request, *args, **kwargs):
        user_list = User.objects.all()
        user_list_serialized = UserSerializer(user_list, many=True)
        if not user_list:
            context = {
                'message': 'NO USERS',
                'status': 204
            }
            return make_response(context)
        context = {
            'message': 'OK',
            'status': 200,
            'data': user_list_serialized.data
        }
        return make_response(context)


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
            return make_response(context)

        # Check if user has logged in or not
        user = get_user(request)
        if not user.is_anonymous:
            context = {
                'message': 'USER ALREADY LOGGED IN.',
                'status': 400
            }
            return make_response(context)

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
            return make_response(context)

        # Skipped checking if user is active or not, user is active by default so I make this simpler

        login(request, user)
        previous_token, _ = Token.objects.get_or_create(user=get_user(request))
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
        return make_response(context)


class Logout(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (CusCheckIsAuthenticated,)

    def get(self, request):
        user = get_user(request)
        if user.is_anonymous:
            context = {
                'message': 'ANONYMOUS USER.',
                'status': 404
            }
            return Response(context, status=context['status'])

        token = Token.objects.filter(user=user).first()
        if not token:
            context = {
                'message': 'CANNOT FIND TOKEN',
                'status': 500
            }
            return make_response(context)

        expire_token(token)
        user.user_token = ''
        user.save()
        logout(request=request)

        context = {
            'message': "TOKEN DELETED.",
            'status': 200,
            'data': UserSerializer(user).data
        }
        return make_response(context)


class DeleteCurrentUser(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (CusCheckIsAuthenticated,)

    def delete(self, request):
        data = request.data
        Logger().info(
            '{} user pk={}'.format('DELETE', data)
        )

        current_user = get_user(request)
        user = User.objects.filter(pk=current_user.pk).first()
        if user:
            user.delete()

        context = {
            'message': 'OK',
            'status': 204
        }
        return make_response(context)


class CurrentUser(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        if user.is_anonymous:
            context = {
                'message': 'ANONYMOUS USER.',
                'status': 404,
            }
            return make_response(context)
        context = {
            'message': 'OK',
            'status': 200,
            'data': UserSerializer(user).data
        }
        return make_response(context)
