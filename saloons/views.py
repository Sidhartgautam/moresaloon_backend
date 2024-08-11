from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Saloon, Gallery
from .serializers import SaloonSerializer, GallerySerializer, PopularSaloonSerializer, UserUploadGallerySerializer
from core.utils.pagination import CustomPagination
from core.utils.response import PrepareResponse, exception_response 


class SaloonListView(generics.GenericAPIView):
    serializer_class = SaloonSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        country_code = request.GET.get('country_code')
        queryset = Saloon.objects.all()

        if country_code:
            queryset = queryset.filter(country__code=country_code)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Saloons fetched successfully",
                meta=self.get_paginated_response(serializer.data).data['meta']
            )
            return response.send()

        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Saloons fetched successfully"
        )
        return response.send(200)

class SaloonDetailView(generics.RetrieveAPIView):
    queryset = Saloon.objects.all()
    serializer_class = SaloonSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        saloon = self.get_object()
        serializer = self.get_serializer(saloon)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Saloon details fetched successfully"
        )
        return response.send(200)

class GalleryUploadView(generics.CreateAPIView):
    serializer_class = UserUploadGallerySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Image uploaded successfully"
            )
            return response.send(201)
        return exception_response(serializer.errors)

class PopularSaloonListView(generics.ListAPIView):
    serializer_class = PopularSaloonSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Assuming review_count is calculated elsewhere, e.g., using annotations
        return Saloon.objects.filter(review_count__gt=0).order_by('-review_count')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Popular saloons fetched successfully",
                meta=self.get_paginated_response(serializer.data).data['meta']
            )
            return response.send(200)

        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Popular saloons fetched successfully"
        )
        return response.send(200)
