from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from .search import search
from saloons.serializers import SaloonSerializer
from services.serializers import ServiceSerializer, ServiceVariationSerializer
from staffs.serializers import StaffSerializer

class SearchView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', None)
        price_min = request.query_params.get('price_min', None)
        price_max = request.query_params.get('price_max', None)
        popular_saloons = request.query_params.get('popular_saloons', None)

        results = search(query, price_min, price_max, popular_saloons)
        
        saloon_serializer = SaloonSerializer(results['saloons'], many=True)
        service_serializer = ServiceSerializer(results['services'], many=True)
        staff_serializer = StaffSerializer(results['staff'], many=True)
        service_variation_serializer = ServiceVariationSerializer(results['service_variations'], many=True)

        response_data = {
            'saloons': saloon_serializer.data,
            'services': service_serializer.data,
            'staff': staff_serializer.data,
            'service_variations': service_variation_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
