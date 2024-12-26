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
    discount_type = serializers.SerializerMethodField()

    class Meta:
        model = SaloonCoupons
        fields = ['id', 'code', 'saloon', 'services', 'percentage_discount', 'fixed_discount', 'start_date', 'end_date', 'is_global', 'discount_type'] 

    def validate(self, data):
        if data.get('is_global') and 'services' in data and data['services']:
            raise serializers.ValidationError("A coupon cannot be both global and specific to services.")
        return data

    def get_discount_type(self, obj):
        if obj.percentage_discount:
            return "percentage"
        elif obj.fixed_discount:
            return "fixed"
        return None

    def create(self, validated_data):
        service_ids = validated_data.pop('services', [])
        coupon = SaloonCoupons.objects.create(**validated_data)
        coupon.services.set(service_ids)
        return coupon
    
class CouponListSerializer(serializers.ModelSerializer):
    discount_type = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    class Meta:
        model = SaloonCoupons
        fields = ['id', 'code', 'percentage_discount', 'fixed_discount', 'start_date', 'end_date', 'is_active', 'is_global','discount_type','services']

    def get_discount_type(self, obj):
        if obj.percentage_discount:
            return "percentage"
        elif obj.fixed_discount:
            return "fixed"
        return None

    def get_is_active(self, obj):
        """Return True if the current time is within the offer's active period."""
        now = timezone.now()
        return obj.start_date <= now <= obj.end_date

class SaloonOfferSerializer(serializers.ModelSerializer):
    percentage_discount = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    fixed_discount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    discount_type = serializers.SerializerMethodField()
    class Meta:
        model = SaloonOffers
        fields = [
            'id',
            'name',
            'saloon',
            'banner',
            'percentage_discount',
            'fixed_discount',
            'discount_type',
            'description',
            'start_offer',
            'end_offer',
        ]
        read_only_fields = ['id']

    def get_discount_type(self, obj):
        if obj.percentage_discount:
            return "percentage"
        elif obj.fixed_discount:
            return "fixed"
        return None

    def validate(self, data):
        if 'end_offer' in data and data['end_offer'] <= timezone.now():
            raise serializers.ValidationError({
                'end_offer': 'End offer date must be in the future.'
            })
        if 'end_offer' in data and data['end_offer'] <= data.get('start_offer', timezone.now()):
            raise serializers.ValidationError({
                'end_offer': 'End offer date must be after the start offer date.'
            })

        if 'percentage_discount' in data and 'fixed_discount' in data:
            raise serializers.ValidationError({
                'percentage_discount': 'Only one of percentage_discount or fixed_discount can be set.',
                'fixed_discount': 'Only one of percentage_discount or fixed_discount can be set.'
            })

        return data