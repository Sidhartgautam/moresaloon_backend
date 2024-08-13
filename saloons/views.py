from math import radians, cos, sin, asin, sqrt
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import Saloon, Gallery
from .serializers import SaloonSerializer, GallerySerializer,PopularSaloonSerializer
from core.utils.pagination import CustomPagination
from core.utils.response import PrepareResponse

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
            return response.send(status.HTTP_201_CREATED)
        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Saloon creation failed"
        )
        return response.send(status.HTTP_400_BAD_REQUEST)

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

class SaloonDetailView(generics.GenericAPIView):
    queryset = Saloon.objects.all()
    serializer_class = SaloonSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get('pk')
        return self.queryset.get(pk=pk)

    def get(self, request, *args, **kwargs):
        saloon = self.get_object()  
        serializer = self.get_serializer(saloon) 
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Saloon details fetched successfully"
        )
        return response.send(status.HTTP_200_OK)

class GalleryUploadView(generics.GenericAPIView):
    serializer_class = GallerySerializer
    permission_classes = [IsAuthenticated]

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
            return response.send(status.HTTP_201_CREATED)
        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Image upload failed"
        )
        return response.send(status.HTTP_400_BAD_REQUEST)
    
class NearestSaloonView(APIView):
    def get(self, request, *args, **kwargs):
        lat1 = float(request.query_params.get('latitude'))
        lon1 = float(request.query_params.get('longitude'))
        
        if lat1 == 0 or lon1 == 0:
            saloons = Saloon.objects.filter(country__code=request.country_code)
            serializer = SaloonSerializer(saloons, many=True)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Nearest Saloons fetched successfully"
            )
        else:
            radius = 10  # Radius in km
            
            def haversine(lon1, lat1, lon2, lat2):
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                r = 6371  # Radius of earth in km
                print(f"Distance: {c * r:.2f} km")
                return c * r

            saloons = Saloon.objects.filter(country__code=request.country_code)
            nearby_saloons = [
                saloon for saloon in saloons
                if haversine(lon1, lat1, saloon.lng, saloon.lat) <= radius
            ]

            serializer = SaloonSerializer(nearby_saloons, many=True)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Nearest Saloons fetched successfully"
            )

        return response.send(200)


class PopularSaloonListView(generics.GenericAPIView):
    serializer_class = PopularSaloonSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Saloon.objects.filter(review_count__gt=0).order_by('-review_count')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Popular saloons fetched successfully",
                meta=paginator.get_paginated_response(serializer.data).data['meta']
            )
            return response.send(status.HTTP_200_OK)
        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Popular saloons fetched successfully"
        )
        return response.send(status.HTTP_200_OK)
