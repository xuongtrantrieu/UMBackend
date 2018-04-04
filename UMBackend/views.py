from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


class APIRoot(APIView):
    def get(self, request, *args, **kwargs):
        return Response('Welcome to my API.')
