from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_jwt.views import JSONWebTokenAPIView

# import jwt
# from datetime import datetime, timedelta
# from .settings import SECRET_KEY
from django.contrib.auth import authenticate

@api_view(['GET',])
def api_root(request, **kwargs):
    return Response('Welcome to my API.')

@api_view(['POST',])
def login(request, **kwargs):
    data = request.data

    email = data.get('email', '').lower()
    if not email:
        context = {
            'status': 400,
            'message': 'USER NOT FOUND.'
        }
        return Response(context, status=context['status'])

    # Check if user has logged in or not
    user = request.user
    if user.is_authenticated:
        context = {
            'message': 'USER ALREADY LOGGED IN',
            'status': 400
        }
        return Response(context, status=context['status'])

    password = data.get('password', '')
    user = authenticate(email=email, password=password)
    if not user:
        context = {
            'message': 'INCORRECT LOGIN INFORMATION',
            'status': 400
        }
        return Response(context, status=context['status'])


    context = {
        'message': 'OK',
        'status': 200,
        'data': {
            'token': user.token()
        }
    }
    user.save()
    
    return Response(context, status=context['status'])

# class Login(JSONWebTokenAPIView):
