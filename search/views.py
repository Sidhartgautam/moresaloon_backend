from rest_framework.response import Response
from rest_framework.views import APIView
from saloons.models import Saloon
from services.models import Service, ServiceVariation
from rest_framework import status
from rest_framework.generics import GenericAPIView
from .search import search
from fuzzywuzzy import process
from saloons.serializers import SaloonSerializer
from services.serializers import SearchServiceSerializer, NestedServiceVariationSerializer
from staffs.serializers import StaffSerializer

class SearchView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', None)
        price_min = request.query_params.get('price_min', None)
        price_max = request.query_params.get('price_max', None)
        preferences = request.query_params.get('preferences', None)
        location = request.query_params.get('location', None) 
        country_id = request.query_params.get('country_id', None)
        amenities = request.query_params.getlist('amenities[]', None)
        sort_price = request.query_params.get('sort_price', None)
        ratings = request.query_params.get('ratings',None)
        discount_percentage = request.query_params.get('discount_percentage', None)

        results = search(
            query=query, 
            price_min=price_min, 
            price_max=price_max, 
            preferences=preferences,
            location=location,
            country_id=country_id,
            amenities = amenities,
            sort_price = sort_price,
            discount_percentage = discount_percentage,
            ratings= ratings
        )
        
        if results is None:
            return Response({'message': 'No results found'}, status=status.HTTP_200_OK)

        saloon_serializer = SaloonSerializer(results.get('saloons', []), many=True)
        service_serializer = SearchServiceSerializer(results.get('services', []), many=True)
        staff_serializer = StaffSerializer(results.get('staff', []), many=True)
        service_variation_serializer = NestedServiceVariationSerializer(results.get('service_variations', []), many=True)


        response_data = {
            'saloons': saloon_serializer.data,
            'services': service_serializer.data,
            'staff': staff_serializer.data,
            'service_variations': service_variation_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

class SimilarTermsView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', '')

        if not query:
            return Response({'similar_terms': []}, status=status.HTTP_200_OK)

        # Fetch distinct names from Saloons, Services, and Service Variations
        saloon_names = list(Saloon.objects.values_list('name', flat=True).distinct())
        service_names = list(Service.objects.values_list('name', flat=True).distinct())
        service_variation_names = list(ServiceVariation.objects.values_list('name', flat=True).distinct())

        # Combine all names into one list
        all_names = saloon_names + service_names + service_variation_names

        # Find similar terms using fuzzy matching
        similar_terms = process.extract(query, all_names, limit=10)
        suggestions = [term for term, score in similar_terms if score > 70]  # Terms with score > 70

        return Response({'similar_terms': suggestions}, status=status.HTTP_200_OK)