from rest_framework import serializers
from .models import SaloonOffer
from services.models import ServiceVariation
from services.serializers import ServiceVariationSerializer
from saloons.models import Saloon
from django.utils import timezone

class SaloonOfferSerializer(serializers.ModelSerializer):
    service_variation_ids = serializers.ListField()
    currency_symbol = serializers.SerializerMethodField(read_only=True)
    saloon = serializers.PrimaryKeyRelatedField(queryset=Saloon.objects.all())

    class Meta:
        model = SaloonOffer
        fields = ['name','saloon','service_variation_ids', 'price', 'description', 'banner', 'start_offer', 'end_offer', 'currency_symbol']

    def get_currency_symbol(self, obj):
        return obj.saloon.currency.symbol
    
    def validate(self, data):
        if 'end_offer' in data and data['end_offer'] <= timezone.now():
            raise serializers.ValidationError("End offer date must be after the current date and time.")
        
        saloon = data['saloon']
        print(saloon)
        service_variation_ids = data.get('service_variation_ids',[]) 
        print(service_variation_ids)
        for service_variation_id in service_variation_ids:
            if service_variation_id.service.saloon != saloon:
                raise serializers.ValidationError({
                    'service': f"The service_variation '{service_variation_id.name}' does not belong to the selected saloon '{saloon.name}'."
                })
        return data
    
    def create(self, validated_data):
        service_variation_ids = validated_data.pop('service_variation') 
        saloon_offer = SaloonOffer.objects.create(**validated_data)   
        saloon_offer.service_variation.set(service_variation_ids)        
        return saloon_offer
    
class ServiceVariationListSerializer(serializers.ModelSerializer):
    service_variation_id = serializers.SerializerMethodField()
    class Meta:
        model = ServiceVariation
        fields = ['service_variation_id', 'name']

    def get_service_variation_id(self, obj):
        return obj.id

class SaloonOfferListSerializer(serializers.ModelSerializer):
    service_variation = ServiceVariationListSerializer(many=True)

    class Meta:
        model = SaloonOffer
        fields = ['id','name','service_variation', 'price', 'description', 'banner', 'start_offer', 'end_offer']


     