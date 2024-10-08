from math import radians, cos, sin, asin, sqrt
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Saloon,Gallery
from .serializers import SaloonSerializer, GallerySerializer,PopularSaloonSerializer,SaloonDetailSerializer
from core.utils.pagination import CustomPageNumberPagination
from core.utils.response import PrepareResponse
from django.db.models import Count, Q
from datetime import timedelta
from django.utils.timezone import now


class SaloonCreateView(generics.GenericAPIView):
    serializer_class = SaloonSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            saloon = serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Saloon created successfully"
            )
            return response.send(201)
        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Saloon creation failed"
        )
        return response.send(400)

class SaloonListView(generics.GenericAPIView):
    serializer_class = SaloonSerializer
    pagination_class = CustomPageNumberPagination
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        country_code = request.GET.get('country_code')
        selected_service_ids = request.GET.getlist('selectedServiceIds[]')
        queryset = Saloon.objects.all()

        if country_code:
            queryset = queryset.filter(country__code=country_code)
        if selected_service_ids:
            queryset = queryset.filter(services__id__in=selected_service_ids).distinct()

        paginator = self.pagination_class()
        queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)

        result = paginated_data['results']
        del paginated_data['results']

        response = PrepareResponse(
            success=True,
            message="Saloons fetched successfully",
            data=result,
            meta=paginated_data
        )
        return response.send(code=200)

class SaloonDetailView(generics.GenericAPIView):
    queryset = Saloon.objects.all()
    serializer_class = SaloonDetailSerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        saloon_id = self.kwargs.get('saloon_id')
        print(saloon_id)
        return self.queryset.get(id=saloon_id)

    def get(self, request, *args, **kwargs):
        saloon = self.get_object()  
        serializer = self.get_serializer(saloon) 
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Saloon details fetched successfully"
        )
        return response.send(200)

class GalleryUploadView(generics.GenericAPIView):
    serializer_class = GallerySerializer
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data.update(request.FILES)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Image uploaded successfully"
            )
            return response.send(201)
        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Image upload failed"
        )
        return response.send(400)
    
class GalleryListView(generics.GenericAPIView):
    serializer_class = GallerySerializer
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        saloon_id = self.kwargs.get('saloon_id')
        queryset = Gallery.objects.filter(saloon_id=saloon_id).order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Images fetched successfully"
        )
        return response.send(200)
    
    
class NearestSaloonView(APIView):
    serializer_class = SaloonSerializer
    pagination_class = CustomPageNumberPagination

    def get(self, request, *args, **kwargs):
        lat1 = request.query_params.get('latitude')
        lon1 = request.query_params.get('longitude')
        if not lat1 or not lon1:
            response = PrepareResponse(
                success=False,
                data=[],
                message="Latitude and Longitude not provided",
                errors={"non_field_errors": ["Latitude and Longitude not provided"]}
            )
            return response.send(400)
        try:
            lat1 = float(lat1)
            lon1 = float(lon1)
        except ValueError:
            response = PrepareResponse(
                success=False,
                data=[],
                message="Invalid latitude or longitude format",
                errors={"non_field_errors": ["Invalid latitude or longitude format"]}
            )
            return response.send(400)

        radius = 10  
        def haversine(lon1, lat1, lon2, lat2):
            from math import radians, sin, cos, sqrt, asin
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * asin(sqrt(a))
            r = 6371 
            return c * r

        saloons = Saloon.objects.filter(country__code=request.country_code)
        nearby_saloons = [
            {'saloon': saloon, 'distance': haversine(lon1, lat1, saloon.lng, saloon.lat)}
            for saloon in saloons
            if haversine(lon1, lat1, saloon.lng, saloon.lat) <= radius
        ]
        nearby_saloons.sort(key=lambda x: x['distance'])
        sorted_saloons = [entry['saloon'] for entry in nearby_saloons]
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(sorted_saloons, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)

        result = paginated_data['results']
        del paginated_data['results'] 
        response = PrepareResponse(
            success=True,
            message="Nearest Saloons fetched successfully",
            data=result,
            meta=paginated_data,
        )
        return response.send(200)


class PopularSaloonListView(generics.GenericAPIView):
    serializer_class = PopularSaloonSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        filter_by = self.request.query_params.get('filter', 'all').lower()
        today = now().date()
        queryset = Saloon.objects.annotate(appointment_count=Count('appointment'))

        if filter_by == 'week':
            start_date = today - timedelta(days=7)
            queryset = queryset.annotate(
                recent_appointment_count=Count(
                    'appointment',
                    filter=Q(appointment__date__gte=start_date)
                )
            ).order_by('-recent_appointment_count')

        elif filter_by == 'month':
            queryset = queryset.annotate(
                recent_appointment_count=Count(
                    'appointment',
                    filter=Q(appointment__date__year=today.year, appointment__date__month=today.month)
                )
            ).order_by('-recent_appointment_count')

        elif filter_by == 'year':
            queryset = queryset.annotate(
                recent_appointment_count=Count(
                    'appointment',
                    filter=Q(appointment__date__year=today.year)
                )
            ).order_by('-recent_appointment_count')

        else:
            queryset = queryset.order_by('-appointment_count')

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(queryset, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)

        result = paginated_data['results']
        del paginated_data['results']

        response = PrepareResponse(
            success=True,
            message="Saloons fetched successfully",
            data=result,
            meta=paginated_data
        )
        return response.send(code=200)
