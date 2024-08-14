from rest_framework import generics
from saloons.models import Saloon
from rest_framework.permissions import IsAuthenticated
from .models import ServiceCategory, Service
from .serializers import ServiceCategorySerializer, ServiceSerializer, ServiceImageSerializer
from core.utils.pagination import CustomPageNumberPagination
from core.utils.response import PrepareResponse

class ServiceCategoryListView(generics.GenericAPIView):
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return ServiceCategory.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(page, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)
        result = paginated_data['results']
        del paginated_data['results']

        # Prepare the response
        response = PrepareResponse(
            success=True,
            message="Service categories fetched successfully",
            data=result,
            meta=paginated_data
        )
        return response.send(code=200)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Service category created successfully"
            )
            return response.send(201)
        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to create service category"
        )
        return response.send(400)

class ServiceListView(generics.GenericAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination 

    def get_queryset(self):
        saloon_id = self.kwargs.get('saloon_id')
        queryset = Service.objects.all()
        if saloon_id:
            queryset = queryset.filter(saloon_id=saloon_id)
        return queryset
    def get(self, request, *args, **kwargs):
        saloon_id = self.kwargs.get('saloon_id')
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)
        result = paginated_data['results']
        del paginated_data['results']

        response = PrepareResponse(
            success=True,
            data=result,
            message="Services fetched successfully",
            meta=paginated_data
        )
        return response.send(code=200)

    def post(self, request, *args, **kwargs):
        saloon_id = self.kwargs.get('saloon_id')
        if not saloon_id:
            response = PrepareResponse(
                success=False,
                data={},
                message="saloon_id is required"
            )
            return response.send(400)

        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(saloon_id=saloon_id)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Service added successfully"
            )
            return response.send(201)

        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to add service"
        )
        return response.send(400)

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

class ServiceImageUploadView(generics.GenericAPIView):
    serializer_class = ServiceImageSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if 'image' in request.FILES:
            request.data._mutable = True
            request.data['image'] = request.FILES['image']       
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Service image uploaded successfully"
            )
            return response.send(201)
        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to upload service image"
        )
        return response.send(400)
