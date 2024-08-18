from rest_framework import serializers
from .models import SaloonOffer
from services.serializers import ServiceSerializer
from saloons.models import Saloon

class SaloonOfferSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(many=True)
    currency_symbol = serializers.SerializerMethodField(read_only=True)
    saloon = serializers.PrimaryKeyRelatedField(queryset=Saloon.objects.all())

    class Meta:
        model = SaloonOffer
        fields = ['name','saloon','service', 'price', 'description', 'banner', 'start_offer', 'end_offer', 'currency_symbol']

    def get_currency_symbol(self, obj):
        return obj.saloon.currency.symbol
    
    def validate(self, data):
        if data['end_offer'] <= data['start_offer']:
            raise serializers.ValidationError("End offer date must be after the start offer date.")
        
        saloon = data['saloon']
        services = data['service']
        for service in services:
            if service.saloon != saloon:
                raise serializers.ValidationError({
                    'service': f"The service '{service.name}' does not belong to the selected saloon '{saloon.name}'."
                })
        return data
    
    def create(self, validated_data):
        services = validated_data.pop('service')
        saloon_offer = SaloonOffer.objects.create(**validated_data)
        saloon_offer.service.set(services)
        return saloon_offer