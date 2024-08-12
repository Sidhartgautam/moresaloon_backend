from rest_framework import generics
from .search import search
from saloons.serializers import SaloonSerializer
from services.serializers import ServiceSerializer
from staffs.serializers import StaffSerializer
from core.utils.response import PrepareResponse

class SaloonSearchView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', None)
        category = request.query_params.get('category', None)
        price_min = request.query_params.get('price_min', None)
        price_max = request.query_params.get('price_max', None)
        popular_saloons = request.query_params.get('popular_saloons', None)

        results = search(query, category, price_min, price_max, popular_saloons)
        saloon_serializer = SaloonSerializer(results['saloons'], many=True)
        service_serializer = ServiceSerializer(results['services'], many=True)
        staff_serializer = StaffSerializer(results['staff'], many=True)

        response = PrepareResponse(
            success=True,
            data={
                'saloons': saloon_serializer.data,
                'services': service_serializer.data,
                'staff': staff_serializer.data
            },
            message="Search results fetched successfully"
        )
        return response.send(200)
