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
