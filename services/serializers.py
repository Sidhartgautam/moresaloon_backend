from rest_framework import serializers
from .models import ServiceCategory, Service, ServiceImage
from saloons.models import Saloon

class ServiceCategorySerializer(serializers.ModelSerializer):
    saloon = serializers.PrimaryKeyRelatedField(queryset=Saloon.objects.all())
    description = serializers.CharField()
    class Meta:
        model = ServiceCategory
        fields = ['id','name', 'description', 'saloon']

class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImage
        fields = ('image','service')

class ServiceSerializer(serializers.ModelSerializer):
    images = ServiceImageSerializer(many=True, read_only=True)
    category =serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all())
    description = serializers.CharField()
    
    
    class Meta:
        model = Service
        fields = ['id', 'category', 'name', 'description', 'duration', 'price', 'images']

class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['saloon', 'category', 'name', 'description', 'duration', 'price']
