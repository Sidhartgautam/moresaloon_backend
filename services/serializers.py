from rest_framework import serializers
from .models import  Service, ServiceImage, ServiceVariation,ServiceVariationImage
from saloons.models import Saloon


class ServiceVariationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    saloon = serializers.SerializerMethodField() 
    class Meta:
        model = ServiceVariation
        fields = ['id', 'name','saloon','duration','price','description','image']

    def get_image(self, obj):
        image = ServiceVariationImage.objects.filter(variation=obj).first()  # 'variation=obj' instead of 'service=obj.service'
        return image.image.url if image else None
    def get_saloon(self, obj):
       return obj.service.saloon.id if obj.service and obj.service.saloon else None


class ServiceVariationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceVariationImage
        fields = ['image']

    def get_image(self, obj):
        return obj.image.url
    
class ServiceImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ServiceImage
        fields = ['image']

    def get_image(self, obj):        
        return obj.image.url



class ServiceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    description = serializers.CharField()
    variations = ServiceVariationSerializer(many=True, read_only=True)
    class Meta:
        model = Service
        fields = ['id','name', 'description','variations', 'min_duration', 'max_duration', 'image','slug']

    def get_image(self, obj):
        image = ServiceImage.objects.filter(service=obj).first()
        return image.image.url if image else None

class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['saloon', 'name', 'description', 'duration', 'price']

class NestedServiceVariationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    saloon_id = serializers.SerializerMethodField(read_only=True) 
    service_id = serializers.SerializerMethodField(read_only=True)   
    class Meta:
        model = ServiceVariation
        fields =['id','saloon_id','service_id','name','price','image','description','duration']

    def get_saloon_id(self, obj):
        return obj.service.saloon.id
    
    def get_service_id(self, obj):
        return obj.service.id

    def get_image(self, obj):
        image = ServiceVariationImage.objects.filter(variation=obj).first()
        return image.image.url if image else None
    
class NestedServiceSerializer(serializers.ModelSerializer):#service category
    variations = serializers.SerializerMethodField(read_only=True)
    image = ServiceImageSerializer(read_only=True)
    class Meta:
        model = Service
        fields = [ 'id','name', 'variations', 'image','slug']

    def get_variations(self, obj):
        saloon = self.context.get('saloon')
        variations = ServiceVariation.objects.filter(service=obj, service__saloon=saloon)
        return NestedServiceVariationSerializer(variations, many=True).data

    def get_image(self, obj):
        image = ServiceImage.objects.filter(service=obj).first()
        return image.image.url if image else None
