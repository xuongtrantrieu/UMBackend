from rest_framework.viewsets import generics
from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password



class Users(generics.ListAPIView):
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user_list = User.objects.all()
        user_list_serialized = self.serializer_class(user_list)

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

    def post(self, request, *args, **kwargs):
        data = request.data
        user_serialized = self.serializer_class(data=data)

        if not user_serialized.is_valid():
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

        context = {
            'data': user_serialized.validated_data,
            'message': 'OK',
            'status': 200
        }

        return Response(context, status=context['status'])
