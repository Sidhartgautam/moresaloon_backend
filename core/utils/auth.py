from rest_framework_simplejwt.authentication import JWTAuthentication
from core.utils.permissions import IsSaloonPermission
from django.shortcuts import get_object_or_404
from rest_framework import status
from core.utils.response import PrepareResponse
from saloons.models import Saloon
class SaloonPermissionMixin(object):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsSaloonPermission,)
    

class NoAuthRequired(object):
    authentication_classes = ()
    permission_classes = ()


__all__ = [
    "SaloonPermissionMixin",
    "NoAuthRequired",
]