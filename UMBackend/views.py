from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.contrib.auth import authenticate, login, logout, get_user
from rest_framework.authtoken.models import Token
from addons.core.users.serializers import UserSerializer
from utils.shortcuts import expire_token, make_response
from lib.logger import Logger


@api_view(['GET', ])
def _api_root():
    return Response('Welcome to my API.')


class CurrentUser(APIView):
    pass





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
