import requests
from django.conf import settings
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()

class SSOAuthentication(JWTAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_header = auth_header.replace('Bearer ', '')
        else:
            return None

        validated_token = self.get_validated_token(auth_header)
        return self.get_or_create_user(auth_header), validated_token

    def get_validated_token(self, auth_header):
        sso_service_url = f"{settings.SSO_SERVICE_URL}auth/verify/token/"
        response = requests.post(sso_service_url, data={'token': auth_header})
        if response.status_code != 200:
            raise InvalidToken("Token is invalid")
        return True

    def get_or_create_user(self, validated_token):
        print(validated_token)
        user_basic_details = f"{settings.SSO_SERVICE_URL}auth/user/all/details/"
        response = requests.get(user_basic_details, headers={'Authorization': f'Bearer {validated_token}'})
        if response.status_code != 200:
            raise InvalidToken("Unable to fetch user details")

        user_data = response.json()
        user_id = user_data['data']['id']
        user_email = user_data['data']['email']
        username = user_data['data']['username']
        first_name = user_data['data']['first_name']
        last_name = user_data['data']['last_name']
        phone_number = user_data['data']['phone_number']


        try:
            user = User.objects.get(Q(email=user_email) | Q(username=username) | Q(phone_number=phone_number))
        except User.DoesNotExist:
            user = User.objects.create(
                id=user_id,
                email=user_email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number
            )

        return user
