from rest_framework import serializers
from .models import ServiceCategory, Service, ServiceImage

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'description', 'saloon']

class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImage
        fields = ('image',)

class ServiceSerializer(serializers.ModelSerializer):
    images = ServiceImageSerializer(many=True, read_only=True)
    category = ServiceCategorySerializer(read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'saloon', 'category', 'name', 'description', 'duration', 'price', 'images']

class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['saloon', 'category', 'name', 'description', 'duration', 'price']
