from rest_framework import generics
from saloons.models import Saloon
from django.db.models import Max
from rest_framework.permissions import IsAuthenticated
from .models import Service,ServiceVariation,ServiceImage
from .serializers import  ServiceSerializer, ServiceImageSerializer, ServiceVariationSerializer, NestedServiceSerializer,AllServiceSerializer
from core.utils.pagination import CustomPageNumberPagination
from core.utils.response import PrepareResponse

class ServiceListView(generics.GenericAPIView):
    serializer_class = ServiceSerializer
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination 

    def get_queryset(self):
        saloon_id = self.kwargs.get('saloon_id')
        country_code = self.request.country_code
        queryset = Service.objects.filter(country__code=country_code)
        if saloon_id:
            queryset = queryset.filter(saloon_id=saloon_id, country_code=country_code)
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

class ServiceDetailView(generics.GenericAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        saloon_id = self.kwargs.get('saloon_id')
        service_id = self.kwargs.get('pk')
        return self.queryset.get(id=service_id, saloon_id=saloon_id)

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
    # permission_classes = [IsAuthenticated]

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

    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     if 'images' not in request.FILES:
    #         response = PrepareResponse(
    #             success=False,
    #             message="No images provided"
    #         )
    #         return response.send(400)
    #     request.data._mutable = True
    #     images = request.FILES.getlist('images')
    #     request.data['images'] = images

    #     serializer = self.get_serializer(data=request.data, many=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         response = PrepareResponse(
    #             success=True,
    #             data=serializer.data,
    #             message="Service images uploaded successfully"
    #         )
    #         return response.send(201)
    #     response = PrepareResponse(
    #         success=False,
    #         data=serializer.errors,
    #         message="Failed to upload service images"
    #     )
    #     return response.send(400)

    
    

class ServiceVariationListView(generics.GenericAPIView):
    serializer_class = ServiceVariationSerializer
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination 

    def get_queryset(self):
        service_id = self.kwargs.get('service_id')
        country_code = self.request.country_code
        queryset = ServiceVariation.objects.filter(service_id=service_id, service__saloon__country__code=country_code).distinct()
        
        if service_id:
            queryset = queryset.filter(service_id=service_id, service__saloon__country__code=country_code)
        return queryset
    def get(self, request, *args, **kwargs):
        service_id = self.kwargs.get('service_id')
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
            message="Service variations fetched successfully",
            meta=paginated_data
        )
        return response.send(code=200)
    
class NestedServiceListView(generics.GenericAPIView):
    serializer_class = NestedServiceSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        country_code = self.request.country_code
        saloon_id = self.kwargs.get('saloon_id')
        if saloon_id:
            return Service.objects.filter(saloon_id=saloon_id, saloon__country__code=country_code)
        return Service.objects.none()

    def get(self, request, *args, **kwargs):
        country_code = self.request.country_code
        saloon_id = self.kwargs.get('saloon_id')
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'saloon': saloon_id})
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Services fetched successfully"
        )
        return response.send(code=200)

class AllServiceListView(generics.GenericAPIView):
    serializer_class = AllServiceSerializer
    pagination_class = CustomPageNumberPagination

    # def get_queryset(self):
    #     return Service.objects.values('id','name').distinct()
    def get_queryset(self):
        queryset = Service.objects.values('name').annotate(
            icon=Max('icon'),
            id=Max('id') 
        ).order_by('name')
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
            data=result,
            message="All services fetched successfully",
            meta=paginated_data
        )
        return response.send(code=200)
