from rest_framework.generics import GenericAPIView
from rest_framework import generics
from .serializers import SaloonOfferSerializer, SaloonOfferListSerializer
from .models import SaloonOffer
from core.utils.response import PrepareResponse
from core.utils.pagination import CustomPageNumberPagination

class SaloonOfferCreateView(generics.GenericAPIView):
    serializer_class = SaloonOfferSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Saloon Offer created successfully"
            )
            return response.send(code=201)

        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to create saloon offer"
        )
        return response.send(code=400)

class SaloonOfferListView(GenericAPIView):
    serializer_class = SaloonOfferListSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        country_code = self.request.country_code
        if country_code:
            queryset = SaloonOffer.objects.filter(saloon__country__code=country_code).order_by('?')[:4]
        else:
            queryset = SaloonOffer.objects.all().order_by('?')[:4]
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)
        result = paginated_data['results']
        del paginated_data['results']
        response = PrepareResponse(
            success=True,
            message="Saloon Offers fetched successfully",
            data=result,
            meta=paginated_data
        )
        return response.send(code=200)

class SaloonSpecificOfferListView(GenericAPIView):
    serializer_class = SaloonOfferListSerializer
    pagination_class = CustomPageNumberPagination

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
        paginator = self.pagination_class()
        queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)
        result = paginated_data['results']
        del paginated_data['results']
        response = PrepareResponse(
            success=True,
            message="Saloon Offers fetched successfully",
            data=result,
            meta=paginated_data
        )
        return response.send(code=200)
