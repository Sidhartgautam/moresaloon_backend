from rest_framework import serializers
from .models import  Service, ServiceImage, ServiceVariation,ServiceVariationImage
from saloons.models import Saloon


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
            return int(((obj.price - obj.discount_price) / obj.price) * 100)
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
    saloon_id = serializers.SerializerMethodField(read_only=True) 
    saloon_name = serializers.SerializerMethodField(read_only=True)
    service_id = serializers.SerializerMethodField(read_only=True)
    address = serializers.SerializerMethodField(read_only=True) 
    discount_percentage = serializers.SerializerMethodField(read_only=True)
    currency_symbol = serializers.SerializerMethodField()
    currency_code=serializers.SerializerMethodField() 
     
    class Meta:
        model = ServiceVariation
        fields =['id','saloon_id','saloon_name','address','service_id','name','price','discount_price','discount_percentage','image','description','duration','currency_symbol','currency_code']

    def get_saloon_id(self, obj):
        return obj.service.saloon.id
    
    def get_saloon_name(self, obj):
        return obj.service.saloon.name
    def get_address(self, obj):
        return obj.service.saloon.address
    
    def get_service_id(self, obj):
        return obj.service.id
    
    def get_discount_percentage(self, obj):
        if obj.discount_price:
            return int(((obj.price - obj.discount_price) / obj.price) * 100)
        else:
            return None

    def get_image(self, obj):
        image = ServiceVariationImage.objects.filter(variation=obj).first()
        return image.image.url if image else None
    def get_currency_symbol(self, obj):
        return obj.service.saloon.currency.symbol
    
    def get_currency_code(self, obj):
        return obj.service.saloon.currency.currency_code

class ServiceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    description = serializers.CharField()
    variations = NestedServiceVariationSerializer(many=True, read_only=True)
    # appointments_count= serializers.IntegerField(read_only=True)
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
    
class AllServiceSerializer(serializers.ModelSerializer):
    # image = serializers.SerializerMethodField()
    class Meta:
        model = Service
        fields = ['id','name' ]

    # def get_image(self, obj):
    #     image = ServiceImage.objects.filter(service=obj).first()
    #     return image.image.url if image else None
