from rest_framework.permissions import BasePermission
import requests
from django.conf import settings
from core.utils.moredealstoken import get_moredeals_token
from rest_framework_simplejwt.authentication import JWTAuthentication



class IsSaloonPermission(BasePermission):    
    def has_permission(self, request, view):
        token = get_moredeals_token(request)
        sso_service_url = f"{settings.SSO_SERVICE_URL}permissions/restaurant/"
        response = requests.get(sso_service_url, headers={'Authorization': f'{token}'})
        if response.status_code == 200:
            return True
        return False
        