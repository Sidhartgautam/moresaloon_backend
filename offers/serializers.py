from rest_framework import serializers
from .models import SaloonCoupons, SaloonOffers
from django.utils import timezone
from saloons.models import Saloon
from services.models import Service


class CouponSerializer(serializers.ModelSerializer):
    services = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="IDs of services the coupon applies to."
    )

    class Meta:
        model = SaloonCoupons
        fields = ['id', 'code', 'saloon', 'services', 'discount_percentage', 'start_date', 'end_date', 'is_global']
        read_only_fields = ['code']  

    def validate(self, data):
        if data.get('is_global') and 'services' in data and data['services']:
            raise serializers.ValidationError("A coupon cannot be both global and specific to services.")
        return data

    def create(self, validated_data):
        service_ids = validated_data.pop('services', [])
        coupon = SaloonCoupons.objects.create(**validated_data)
        coupon.services.set(service_ids)
        return coupon
    

class SaloonOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaloonOffers
        fields = [
            'id',
            'name',
            'saloon',
            'banner',
            'offer_price',
            'description',
            'start_offer',
            'end_offer'
        ]
        read_only_fields = ['id', 'start_offer']

    def validate(self, data):
        if 'end_offer' in data and data['end_offer'] <= timezone.now():
            raise serializers.ValidationError({
                'end_offer': 'End offer date must be in the future.'
            })
        if 'end_offer' in data and data['end_offer'] <= data.get('start_offer', timezone.now()):
            raise serializers.ValidationError({
                'end_offer': 'End offer date must be after the start offer date.'
            })

        return data