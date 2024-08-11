import requests
from rest_framework import generics
from users.models import User
from .serializers import UserSerializer
from decouple import config
from core.utils.response import PrepareResponse

main_api_url = config('MAIN_API_URL')

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class HomeView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Welcome to the protected route!'}
        return Response(content)
