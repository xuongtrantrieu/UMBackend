from django.shortcuts import render
from rest_framework.viewsets import generics
from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response


class UsersView(generics.ListAPIView):
    queryset = User.objects.all()
    # model = User
    serializer_class = UserSerializer

