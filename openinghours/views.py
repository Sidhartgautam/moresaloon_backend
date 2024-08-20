from django.shortcuts import render
from rest_framework import generics
from rest_framework.generics import GenericAPIView
from .models import OpeningHour
from .serializers import OpeningHourSerializer
from core.utils.response import PrepareResponse


class OpeningHoursCreateView(generics.GenericAPIView):
    serializer_class = OpeningHourSerializer

    def post(self,request,*args,**kwargs):
        serializer =self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response=PrepareResponse(
                success=True,
                data=serializer.data,
                message="Opening Hours created successfully"
            )
            return response.send(201)

        response = PrepareResponse( 
            success=False,
            data=serializer.errors,
            message="Failed to create opening hours"
        )
        return response.send(400)   

class OpeningHoursListView(GenericAPIView):
    serializer_class = OpeningHourSerializer

    def get_queryset(self):
        country_code = self.request.country_code
        if country_code:
            queryset = OpeningHour.objects.filter(saloon__country__code=country_code).order_by('?')[:4]
        else:
            queryset = OpeningHour.objects.all().order_by('?')[:4]
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Opening Hours fetched successfully"
        )
        return response.send(200)
    
class OpeningHourRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OpeningHourSerializer

    def get_queryset(self):
        return OpeningHour.objects.all()
    def put (self, request, *args, **kwargs):
        opening_hour = self.get_object()
        serializer = self.get_serializer(opening_hour, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Opening Hours updated successfully"
            )
            return response.send(200)
    def delete(self, request, *args, **kwargs):
        opening_hour = self.get_object()
        opening_hour.delete()
        response = PrepareResponse(
            success=True,
            message="Opening Hours deleted successfully"
        )
        return response.send(200)
    
    def patch (self, request, *args, **kwargs):
        opening_hour = self.get_object()
        serializer = self.get_serializer(opening_hour, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Opening Hours updated successfully"
            )
            return response.send(200)