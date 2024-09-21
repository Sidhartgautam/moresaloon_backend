from rest_framework import serializers
from saloons.models import Saloon
from country.models import Country,Currency
from services.models import Service, ServiceVariation
from services.serializers import ServiceVariationSerializer


####################################USER########################################
class UserNameSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)


####################################SALOON########################################
class SaloonSerializer(serializers.Serializer):
    id=serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    short_description = serializers.CharField(max_length=255)
    long_description = serializers.CharField(max_length=255)
    country_code= serializers.SerializerMethodField()
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())
    currency_code = serializers.SerializerMethodField()
    currency=serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    email = serializers.EmailField()
    logo = serializers.ImageField()
    banner = serializers.ImageField()
    website_link = serializers.CharField(max_length=255)
    facebook_link = serializers.CharField(max_length=255)
    instagram_link = serializers.CharField(max_length=255)
    contact_no = serializers.CharField(max_length=255)


    def get_country_code(self, obj):
        return obj.saloon.country.code

    def get_currency_code(self, obj):
        return obj.saloon.currency.currency_code
    def create(self, validated_data):
        saloon = Saloon.objects.create(**validated_data)
        return Saloon
    def update(self, instance, validated_data):
        instance.country = validated_data.get('country', instance.country)
        instance.currency = validated_data.get('currency', instance.currency)
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.short_description = validated_data.get('short_description', instance.short_description)
        instance.long_description = validated_data.get('long_description', instance.long_description)
        instance.lat = validated_data.get('lat', instance.lat)
        instance.lng = validated_data.get('lng', instance.lng)
        instance.email = validated_data.get('email', instance.email)
        instance.contact_no = validated_data.get('contact_no', instance.contact_no)
        instance.logo = validated_data.get('logo', instance.logo)
        instance.banner = validated_data.get('banner', instance.banner)
        instance.website_link = validated_data.get('website_link', instance.website_link)
        instance.facebook_link = validated_data.get('facebook_link', instance.facebook_link)
        instance.instagram_link = validated_data.get('instagram_link', instance.instagram_link)
        
        instance.save()
        return instance
    
##########################Services###########################

class ServiceVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceVariation
        field=['id','name']



class ServiceSerializer(serializers.ModelSerialzier):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    min_duration = serializers.DurationField()
    max_duration = serializers.DurationField()
    image = serializers.ImageField()
    slug = serializers.SlugField()

    class Meta:
        model = Service
        field=['id','name', 'description', 'min_duration', 'max_duration', 'image','slug']

class ServiceVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model= ServiceVariation
        field=['id','name','price']
        


    
