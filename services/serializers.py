from rest_framework import serializers
from .models import  Service, ServiceImage, ServiceVariation,ServiceVariationImage
from saloons.models import Saloon
from datetime import timedelta
from django.core.cache import cache
from django.utils.decorators import method_decorator


class ServiceVariationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    saloon = serializers.SerializerMethodField() 
    price=serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    currency_symbol = serializers.SerializerMethodField()
    currency_code=serializers.SerializerMethodField()
    class Meta:
        model = ServiceVariation
        fields = ['id', 'name','saloon','duration','price','discount_price','discount_percentage','description','image','currency_symbol','currency_code']

    def get_image(self, obj):
        image = ServiceVariationImage.objects.filter(variation=obj).first()  
        return image.image.url if image else None
    def get_saloon(self, obj):
       return obj.service.saloon.id if obj.service and obj.service.saloon else None
    def get_price(self, obj):
        return float(obj.price)

    def get_dis_price(self, obj):
        if obj.discount_price and obj.discount_price > 0:
            return float(obj.discount_price)
        else:
            return float(obj.price)
    
    def get_discount_percentage(self, obj):
        if obj.discount_price:
            return float(((obj.price - obj.discount_price) / obj.price) * 100)
        else:
            return None
        
    def get_currency_symbol(self, obj):
        return obj.service.saloon.currency.symbol
    
    def get_currency_code(self, obj):
        return obj.service.saloon.currency.currency_code


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

class NestedServiceVariationSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    saloon_id = serializers.ReadOnlyField(source='service.saloon.id')
    saloon_name = serializers.ReadOnlyField(source='service.saloon.name')
    address = serializers.ReadOnlyField(source='service.saloon.address')
    service_id = serializers.ReadOnlyField(source='service.id')
    discount_percentage = serializers.SerializerMethodField()
    currency_symbol = serializers.ReadOnlyField(source='service.saloon.currency.symbol')
    currency_code = serializers.ReadOnlyField(source='service.saloon.currency.currency_code')

    class Meta:
        model = ServiceVariation
        fields = [
            'id', 'saloon_id', 'saloon_name', 'address', 'service_id', 'name', 'price', 
            'discount_price', 'discount_percentage', 'image', 'description', 'duration', 
            'currency_symbol', 'currency_code'
        ]

    def get_discount_percentage(self, obj):
        if obj.discount_price:
            try:
                return round(float(((obj.price - obj.discount_price) / obj.price) * 100),2)
            except ZeroDivisionError:
                return None
        return None

    def get_image(self, obj):
        image = obj.images.first()
        return image.image.url if image else None

class ServiceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    description = serializers.CharField()
    variations = NestedServiceVariationSerializer(many=True, read_only=True)
    min_duration = serializers.SerializerMethodField()
    max_duration = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'variations', 'min_duration', 'max_duration', 'image', 'slug']

    def get_min_duration(self, obj):
        durations = [variation.duration for variation in obj.variations.all() if variation.duration != timedelta(0)]
        if durations:
            min_duration = min(durations) 
            return str(min_duration)
        return None

    def get_max_duration(self, obj):
        durations = [variation.duration for variation in obj.variations.all() if variation.duration != timedelta(0)]
        if durations:
            max_duration = max(durations) 
            return str(max_duration)
        return None

    def get_image(self, obj):
        image = ServiceImage.objects.filter(service=obj).first()
        return image.image.url if image else None

class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['saloon', 'name', 'description', 'duration', 'price']


class NestedServiceSerializer(serializers.ModelSerializer):
    variations = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'variations', 'slug', 'icon']

    def get_variations(self, obj):
        saloon_id = self.context.get('saloon')
        variations = obj.variations.filter(service=obj, service__saloon_id=saloon_id)
        return NestedServiceVariationSerializer(variations, many=True).data


    
class AllServiceSerializer(serializers.Serializer):
    name = serializers.CharField()
    icon = serializers.SerializerMethodField()
    def get_icon(self, obj):
        random_icon = obj.get('random_icon', None)
        if random_icon:
            # Construct full URL if random_icon is a valid path
            return f"https://res.cloudinary.com/dvmqwrhbx/{random_icon}"
        return None
    
class SearchServiceSerializer(serializers.ModelSerializer):
    saloon_name=serializers.CharField(source='saloon.name')
    saloon_id=serializers.CharField(source='saloon.id')
    class Meta:
        model = Service
        fields = ['id', 'name', 'icon','saloon_name','saloon_id','slug']
    
