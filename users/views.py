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
    
class GetUserBalance(generics.GenericAPIView):
    serializer_class = None
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        token = request.headers.get('Authorization')
        url = f"{main_api_url}wallets/get/balance/"
        headers = {
            'Authorization': f"{token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            response = PrepareResponse(
                success=False,
                message="User balance not retrieved"
            )
            return response.send(400)
        
        response = Response(response.json())
        return response
