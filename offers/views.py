from rest_framework.generics import GenericAPIView
from rest_framework import generics
from .serializers import SaloonOfferSerializer
from .models import SaloonOffer
from django.shortcuts import get_object_or_404
from core.utils.response import PrepareResponse


class SaloonOfferCreateView(generics.GenericAPIView):
    serializer_class = SaloonOfferSerializer

    def post(self,request,*args,**kwargs):
        serializer =self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response=PrepareResponse(
                success=True,
                data=serializer.data,
                message="Saloon Offer created successfully"
            )
            return response.send(201)

        response = PrepareResponse( 
            success=False,
            data=serializer.errors,
            message="Failed to create saloon offer"
        )
        return response.send(400)



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
