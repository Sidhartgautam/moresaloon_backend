from rest_framework import serializers
from .models import SaloonOffer
from services.models import ServiceVariation
from services.serializers import ServiceVariationSerializer
from saloons.models import Saloon
from django.utils import timezone

class SaloonOfferSerializer(serializers.ModelSerializer):
    service_variation = serializers.ListField(child=serializers.UUIDField())
    currency_symbol = serializers.SerializerMethodField(read_only=True)
    saloon = serializers.PrimaryKeyRelatedField(queryset=Saloon.objects.all())
    original_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    offer_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    banner = serializers.ImageField(required=False)
    description = serializers.CharField(required=False)

    class Meta:
        model = SaloonOffer
        fields = ['name', 'saloon', 'service_variation', 'original_price', 'offer_price', 'description', 'banner', 'start_offer', 'end_offer', 'currency_symbol']

    def get_currency_symbol(self, obj):
        return obj.saloon.currency.symbol

    def validate(self, data):
        if 'end_offer' in data and data['end_offer'] <= timezone.now():
            raise serializers.ValidationError("End offer date must be after the current date and time.")
        
        saloon = data.get('saloon')
        service_variations = data.get('service_variation', [])

        for service_variation_id in service_variations:
            variation = ServiceVariation.objects.filter(id=service_variation_id).first()
            if variation is None:
                raise serializers.ValidationError(f"ServiceVariation with id {service_variation_id} does not exist.")
            if variation.service.saloon != saloon:
                raise serializers.ValidationError({
                    'service_variation': f"The service variation does not belong to the selected saloon."
                })
            
        return data

    def create(self, validated_data):
        service_variation_ids = validated_data.pop('service_variation', [])
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
        fields = ['id', 'name', 'service_variation', 'original_price', 'offer_price', 'description', 'banner', 'start_offer', 'end_offer']
