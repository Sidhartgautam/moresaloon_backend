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
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_or_create_user(validated_token), validated_token

    def get_validated_token(self, raw_token):
        try:
            token = UntypedToken(raw_token)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        sso_service_url = f"{settings.SSO_SERVICE_URL}auth/verify/token/"
        response = requests.post(sso_service_url, data={'token': raw_token})
        
        if response.status_code != 200:
            raise InvalidToken("Token is invalid")

        return token

    def get_or_create_user(self, validated_token):
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
            # restaurant = Restaurant.objects.create(
            #     name="SOME RANDOM NAME",
            #     lng=0,
            #     lat=0,
            #     address="some random address",
            #     email="some random email",
            #     contact_no="some random contact number",
            #     description="some random description",
            #     banner="some random banner",
            #     logo="some random logo"
            # )
            user = User.objects.create(
                id=user_id,
                email=user_email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number
            )

        return user
