from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ServiceCategory, Service, ServiceImage
from .serializers import ServiceCategorySerializer, ServiceSerializer, ServiceCreateUpdateSerializer, ServiceImageSerializer
from core.utils.pagination import CustomPagination
from core.utils.response import PrepareResponse, exception_response

class ServiceCategoryListView(generics.ListCreateAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Service categories fetched successfully",
                meta=self.get_paginated_response(serializer.data).data['meta']
            )
            return response.send(200)

        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Service categories fetched successfully"
        )
        return response.send(200)

class ServiceListView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        saloon_id = request.GET.get('saloon_id')
        queryset = self.get_queryset()
        if saloon_id:
            queryset = queryset.filter(saloon__id=saloon_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Services fetched successfully",
                meta=self.get_paginated_response(serializer.data).data['meta']
            )
            return response.send(200)

        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Services fetched successfully"
        )
        return response.send(200)

class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        service = self.get_object()
        serializer = self.get_serializer(service)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Service details fetched successfully"
        )
        return response.send(200)

class ServiceImageUploadView(generics.CreateAPIView):
    serializer_class = ServiceImageSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Service image uploaded successfully"
            )
            return response.send(201)
        return exception_response(serializer.errors)
