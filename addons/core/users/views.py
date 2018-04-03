from rest_framework.viewsets import generics
from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from lib.logger import Logger
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.settings import api_settings


class Users(generics.ListAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request):
        user_list = User.objects.all()
        user_list_serialized = self.serializer_class(user_list, many=True).data

        if user_list:
            context = {
                'data': user_list_serialized,
                'message': 'OK',
                'status': 200
            }
        else:
            context = {
                'message': 'NO USERS',
                'status': 204
            }

        return Response(context, status=context['status'])

    def post(self, request):
        data = request.data
        Logger().info(
            '{} user {}'.format('POST', data)
        )
        is_valid = self.serializer_class(data=data).is_valid()

        if not is_valid:
            context = {
                'status': 400,
                'message': 'INVALID INPUT'
            }
            return Response(context, status=context['status'])

        user = User.objects.create(
            email=data['email'],
            password=make_password(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        user.save()

        user_serialized = self.serializer_class(user, many=False).data
        context = {
            'data': user_serialized,
            'message': 'OK',
            'status': 200
        }

        return Response(context, status=context['status'])


class UserDetail(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    # permission_classes = (DjangoObjectPermissions,)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', '')
        user = User.objects.get(pk=pk)

        if not user:
            context = {
                'message': 'USER NOT EXISTS',
                'status': 400
            }
            return Response(context, status=context['status'])

        user_serialized = self.serializer_class(user, many=False).data
        context = {
            'message': 'OK',
            'status': 200,
            'data': user_serialized
        }

        return Response(context, status=context['status'])

    def put(self, request, pk=None):
        data = request.data

        Logger().info(
            '{} user {}'.format('PUT', data)
        )

        is_valid = self.serializer_class(data=data).is_valid()

        if not is_valid:
            context = {
                'message': 'INVALID INPUT DATA',
                'status': 400
            }
            return Response(context, status=context['status'])

        user = User.objects.get(pk=pk)

        if not user:
            context = {
                'message': 'USER NOT EXISTS',
                'status': 400
            }
            return Response(context, status=context['status'])

        # user.email = data['email']
        user.password = make_password(data['password'])
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.save()

        user_serialized = self.serializer_class(user).data

        context = {
            'message': 'OK',
            'status': 200,
            'data': user_serialized
        }
        return Response(context, status=context['status'])

    @staticmethod
    def delete(**kwargs):
        pk = kwargs.get('pk', '')
        Logger().info(
            '{} user pk={}'.format('DELETE', pk)
        )

        user = User.objects.get(pk=pk)
        user.delete()

        context = {
            'message': 'OK',
            'status': 204
        }
        return Response(context, status=context['status'])
