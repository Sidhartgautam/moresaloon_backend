from rest_framework.generics import GenericAPIView
from .serializers import SaloonOfferSerializer
from .models import SaloonOffer
from django.shortcuts import get_object_or_404
from core.utils.response import PrepareResponse

class SaloonOfferListView(GenericAPIView):
    serializer_class = SaloonOfferSerializer

    def get_queryset(self):
        country_code = self.request.country_code
        if country_code:
            queryset = SaloonOffer.objects.filter(saloon__country__code=country_code).order_by('?')[:4]
        else:
            queryset = SaloonOffer.objects.all().order_by('?')[:4]
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Saloon Offers fetched successfully"
        )
        return response.send(200)


class SaloonSpecificOfferListView(GenericAPIView):
    serializer_class = SaloonOfferSerializer

    def get_queryset(self):
        saloon_id = self.kwargs['saloon_id']
        country_code = self.request.country_code
        if country_code:
            queryset = SaloonOffer.objects.filter(saloon__id=saloon_id, saloon__country__code=country_code)
        else:
            queryset = SaloonOffer.objects.filter(saloon__id=saloon_id)
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Saloon Specific Offers fetched successfully"
        )
        return response.send(200)
