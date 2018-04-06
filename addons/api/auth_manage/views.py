from rest_framework.decorators import api_view
from rest_framework.views import APIView
from addons.core.users.models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from lib.logger import Logger
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from utils.shortcuts import make_response, expired_or_not
from rest_framework_jwt.authentication import get_authorization_header
from rest_framework.authentication import authenticate
from rest_framework.authtoken.models import Token
from rest_framework_jwt.settings import api_settings
from utils.permissions import CusCheckIsAuthenticated
from inspect import stack
from UMBackend import settings as my_settings
from utils.authentications import Authentication


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
logger = Logger()
model = User.__name__.lower()


class Register(APIView):
    # permission_classes = (CusCheckIsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        data = request.data

        logger.info(
            '{_class} {method} {object} {data}'.format(
                method=stack()[0][3], _class=self.__class__.__name__,
                object=model,
                data=data)
        )

        authorization = get_authorization_header(request)
        if authorization:
            context = {
                'message': 'THERE IS CURRENTLY A USER ALREADY HAS LOGGED IN.',
                'status': 400
            }
            return make_response(context)

        is_valid = UserSerializer(data=data).is_valid()

        if not is_valid:
            email = data.get('email', '')
            user = User.objects.filter(email=email).first()
            if user and user.is_active:
                context = {
                    'status': 400,
                    'message': 'THIS EMAIL IS ALREADY IN USED.'
                }
                return make_response(context)

        data['password'] = make_password(data['password'])
        user, _ = User.objects.update_or_create(
            email=data.get('email', ''),
            defaults=data
        )
        user.is_active = True
        user.save()

        user_serialized = UserSerializer(user, many=False)
        context = {
            'data': user_serialized.data,
            'message': 'OK',
            'status': 200
        }

        return make_response(context)


class EditCurrentUser(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)

    def put(self, request):
        data = request.data

        logger.info(
            '{_class} {method} {object} {data}'.format(
                method=stack()[0][3], _class=self.__class__.__name__,
                object=model,
                data=data)
        )

        authorization = get_authorization_header(request)
        current_token = ''
        if authorization:
            current_token = authorization.split()[1]
        if not current_token:
            context = {
                'message': "ANONYMOUS USER.",
                'status': 400
            }
            return make_response(context)

        current_user = request.user
        if current_user.is_anonymous:
            context = {
                'message': 'ANONYMOUS USER.',
                'status': 400
            }
            return make_response(context)
        user = User.objects.filter(pk=current_user.pk).first()

        email = data.get('email', '')
        if user.email != email and len(User.objects.filter(email=email)) == 1:
            context = {
                'message': 'THIS EMAIL IS ALREADY IN USED.',
                'status': 400,
                'data': data
            }
            return make_response(context)

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
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request):
        data = request.data
        logger.info(
            '{_class} {method} {object} {data}'.format(
                method=stack()[0][3], _class=self.__class__.__name__,
                object=model,
                data=data)
        )
        user_list = User.objects.filter(is_active=True)
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

    def post(self, request):
        data = request.data
        email = data.get('email', '').lower()
        password = data.get('password', '')

        logger.info(
            '{_class} {method} {object} {data}'.format(
                method=stack()[0][3], _class=self.__class__.__name__,
                object=model,
                data=data)
        )

        user = User.objects.filter(email=email).first()
        if not user.check_password(password):
            context = {
                'message': 'INVALID LOGIN INFORMATION',
                'status': 400
            }
            return make_response(context)

        previous_token, _ = Token.objects.get_or_create(user=user)
        previous_token.delete()

        # create token objects validated by user
        token = Token.objects.create(user=user)
        # save the same token into user_token using the same validation is user
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.user_token = token

        user.is_active = True
        user.save()


        # if user:
        #     Logger().info(
        #         '{} user {}'.format('LOGIN', data)
        #     )
        #     context = {
        #         'message': 'INCORRECT LOGIN INFORMATION.',
        #         'status': 400,
        #     }
        #     return make_response(context)

        # Skipped checking if user is active or not, user is active by default so I make this simpler

        # request.session.set_expiry(10)
        # login(request, user)

        context = {
            'message': 'OK',
            'status': 200,
            'data': UserSerializer(user).data
        }
        return make_response(context)


class Logout(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    # permission_classes = (CusCheckIsAuthenticated,)

    def get(self, request):
        logger.info(
            '{_class} {method} {object}'.format(
                method=stack()[0][3], _class=self.__class__.__name__,
                object=model)
        )

        authorization = get_authorization_header(request)
        current_token = ''
        if authorization:
            current_token = authorization.split()[1]
        if not current_token:
            context = {
                'message': "ANONYMOUS USER.",
                'status': 400
            }
            return make_response(context)

        user = request.user
        token = Token.objects.filter(user=user).first()
        token.delete()
        user.save()

        context = {
            'message': "LOGOUT SUCCESSFULLY.",
            'status': 200,
            'data': UserSerializer(user).data
        }
        return make_response(context)


class DeleteCurrentUser(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    # permission_classes = (CusCheckIsAuthenticated,)

    def delete(self, request):
        # data = request.data
        logger.info(
            '{_class} {method} {object}'.format(
                method=stack()[0][3], _class=self.__class__.__name__,
                object=model)
        )

        current_user = request.user
        if not current_user:
            context = {
                'message': 'ANONYMOUS USER.',
                'status': 400
            }
            return make_response(context)

        user = User.objects.filter(pk=current_user.pk).first()
        if not user:
            context = {
                'message': 'USER IS NOT IN DB :O.',
                'status': 500
            }
        user.is_active = False
        user.save()

        context = {
            'message': 'DELETE USER SUCCESSFULLY.',
            'status': 204
        }
        return make_response(context)


class CurrentUser(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, *args, **kwargs):
        logger.info(
            '{_class} {method} {object}'.format(
                method=stack()[0][3], _class=self.__class__.__name__,
                object=model)
        )

        authorization = get_authorization_header(request)
        current_token = ''
        if authorization:
            current_token = authorization.split()[1]
        if not current_token:
            context = {
                'message': "ANONYMOUS USER.",
                'status': 400
            }
            return make_response(context)

        user = request.user
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
