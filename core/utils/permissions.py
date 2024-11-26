from rest_framework.permissions import BasePermission
import requests
from django.conf import settings
from core.utils.moredealstoken import get_moredeals_token



class IsSaloonPermission(BasePermission):    
    def has_permission(self, request, view):
        token = get_moredeals_token(request)
        sso_service_url = f"https://moretrek.com/api/permissions/saloon/"
        # sso_service_url = f"http://192.168.1.73:8001/api/permissions/saloon/"
        response = requests.get(sso_service_url, headers={'Authorization': f'{token}'})
        if response.status_code == 200:
           return True
        return False
    # f"{settings.SSO_SERVICE_URL}
        