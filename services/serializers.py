from rest_framework import serializers
from .models import ServiceCategory, Service, ServiceImage, ServiceVariation
from saloons.models import Saloon


class ServiceVariationSerializer(serializers.ModelSerializer):
    total_duration = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ServiceVariation
        fields = ['id', 'name', 'additional_duration', 'total_duration']
class ServiceCategorySerializer(serializers.ModelSerializer):
    # saloon = serializers.PrimaryKeyRelatedField(queryset=Saloon.objects.all())
    # description = serializers.CharField()
    class Meta:
        model = ServiceCategory
        # fields = ['id','name', 'description', 'saloon']
        fields = ['name','slug']

class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImage
        fields = ('image','service')

    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     images = request.FILES.getlist('images')
    #     service_id = validated_data.get('service')
    #     created_images = []
        
    #     for image in images:
    #         service_image = ServiceImage.objects.create(
    #             image=image,
    #             service=service_id
    #         )
    #         created_images.append(service_image)
        
    #     return created_images

class ServiceSerializer(serializers.ModelSerializer):
    images = ServiceImageSerializer(many=True, read_only=True)
    category =serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all())
    description = serializers.CharField()
    variations = ServiceVariationSerializer(many=True, read_only=True)
    class Meta:
        model = Service
        fields = ['id','name','category', 'description','variations', 'base_duration', 'price', 'images']

class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['saloon', 'category', 'name', 'description', 'duration', 'price']

class NestedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id','name','category', 'description','variations', 'base_duration', 'price']


class NestedServiceCategorySerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ServiceCategory
        fields = [ 'name', 'services']

    def get_services(self, obj):
        saloon = self.context.get('saloon')
        services = Service.objects.filter(category=obj, saloon=saloon)
        return NestedServiceSerializer(services, many=True).data
