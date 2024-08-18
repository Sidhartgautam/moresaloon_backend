from rest_framework import serializers
from .models import ServiceCategory, Service, ServiceImage, ServiceVariation
from saloons.models import Saloon


class ServiceVariationSerializer(serializers.ModelSerializer):
    total_duration = serializers.SerializerMethodField(read_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ServiceVariation
        fields = ['id', 'name', 'additional_duration', 'total_duration', 'additional_price', 'total_price']

    def get_total_duration(self, obj):
        return obj.total_duration

    def get_total_price(self, obj):
        return obj.total_price
class ServiceCategorySerializer(serializers.ModelSerializer):
    # saloon = serializers.PrimaryKeyRelatedField(queryset=Saloon.objects.all())
    # description = serializers.CharField()
    class Meta:
        model = ServiceCategory
        # fields = ['id','name', 'description', 'saloon']
        fields = ['name','slug']

class ServiceImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ServiceImage
        fields = ['image']

    def get_image(self, obj):        
        return obj.image.url

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     if isinstance(representation, list):
    #         return [self.get_image(item) for item in representation]
    #     return self.get_image(instance)

class ServiceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    category =serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all())
    description = serializers.CharField()
    variations = ServiceVariationSerializer(many=True, read_only=True)
    class Meta:
        model = Service
        fields = ['id','name','category', 'description','variations', 'base_duration', 'price', 'image']

    def get_image(self, obj):
        image = ServiceImage.objects.filter(service=obj).first()
        return image.image.url if image else None

class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['saloon', 'category', 'name', 'description', 'duration', 'price']

class NestedServiceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Service
        fields =['id','name','price','image']

    def get_image(self, obj):
        image = ServiceImage.objects.filter(service=obj).first()
        return image.image.url if image else None
    
class NestedServiceCategorySerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField(read_only=True)
    image = ServiceImageSerializer(read_only=True)
    class Meta:
        model = ServiceCategory
        fields = [ 'id','name', 'services', 'image']

    def get_services(self, obj):
        saloon = self.context.get('saloon')
        services = Service.objects.filter(category=obj, saloon=saloon)
        return NestedServiceSerializer(services, many=True).data
    
    def get_image(self, obj):
        images = ServiceImage.objects.filter(service__category=obj)
        return images.first().image.url if images.exists() else None
