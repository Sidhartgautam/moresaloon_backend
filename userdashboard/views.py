from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from core.utils.response import PrepareResponse
from users.models import User
from saloons.models import Saloon
from services.models import ServiceVariation
from staffs.models import Staff

class StatisticsCounterView(GenericAPIView):
    serializer_class = None

    def get(self, request, *args, **kwargs):
        no_of_users=User.objects.all().count()
        no_of_saloons=Saloon.objects.all().count()
        no_of_service_variations=ServiceVariation.objects.all().count()
        no_of_staffs=Staff.objects.all().count()
        data={
            "no_of_users":no_of_users,
            "no_of_saloons":no_of_saloons,
            "no_of_service_variations":no_of_service_variations,
            "no_of_staffs":no_of_staffs
        }
        response = PrepareResponse(
            success=True,
            data=data,
            message="Statistics fetched successfully"
        )
        return response.send(200)