from rest_framework.viewsets import generics
from addons.core.users.models import User
from addons.core.users.serializers import UserSerializer
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from lib.logger import Logger
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from utils.shortcuts import make_response
from django.contrib.auth import get_user


class Register(generics.ListAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JSONWebTokenAuthentication,)

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


class EditCurrentUser(generics.ListAPIView):
    authentication_classes = (JSONWebTokenAuthentication,)

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


class Login(generics.ListAPIView):
    pass


class Logout(generics.ListAPIView):
    pass


class DeleteCurrentUser(generics.ListAPIView):
    def delete(self, request, pk=None):
        Logger().info(
            '{} user pk={}'.format('DELETE', pk)
        )

        user = User.objects.filter(pk=pk).first()
        if user:
            user.delete()

        context = {
            'message': 'OK',
            'status': 204
        }
        return make_response(context)


class CurrentUser(generics.ListAPIView):
    @staticmethod
    def get(request):
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
