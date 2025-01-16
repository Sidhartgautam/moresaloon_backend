from rest_framework import serializers
from django.utils import timezone
from saloons.models import Saloon,Gallery
from country.models import Country,Currency
from staffs.models import Staff, WorkingDay
from services.models import Service, ServiceVariation, ServiceImage, ServiceVariationImage
from services.serializers import ServiceVariationSerializer
from appointments.models import Appointment, AppointmentSlot
from appointments.serializers import AppointmentSlotSerializer
from openinghours.models import OpeningHour
from offers.models import SaloonOffers,SaloonCoupons
from core.utils.response import PrepareResponse
from datetime import datetime, timedelta

import uuid
from django.core.exceptions import ValidationError


####################################USER########################################
class UserNameSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)


####################################SALOON########################################
class SaloonSerializer(serializers.ModelSerializer):
    # We can add read-only fields for country and currency codes if needed
    country_code = serializers.SerializerMethodField(read_only=True)
    currency_code = serializers.SerializerMethodField(read_only=True)
    website_link = serializers.CharField(allow_blank=True, required=False)
    facebook_link = serializers.CharField(allow_blank=True, required=False)
    instagram_link = serializers.CharField(allow_blank=True, required=False)

    # Define amenities as a ListField of CharField to handle list input
    amenities = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    class Meta:
        model = Saloon
        fields = [
            'id', 'name', 'address', 'email', 'contact_no', 'country', 'currency', 'lat', 'lng',
            'short_description', 'long_description', 'website_link', 'facebook_link',
            'instagram_link', 'logo', 'banner', 'amenities', 'country_code', 'currency_code'
        ]
    
    def get_country_code(self, obj):
        return obj.country.code

    def get_currency_code(self, obj):
        return obj.currency.currency_code

    def create(self, validated_data):
        
        saloon = Saloon.objects.create(**validated_data)
        return saloon

    def update(self, instance, validated_data):
        # Update the saloon instance with new data
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.email = validated_data.get('email', instance.email)
        instance.contact_no = validated_data.get('contact_no', instance.contact_no)
        instance.country = validated_data.get('country', instance.country)
        instance.currency = validated_data.get('currency', instance.currency)
        instance.lat = validated_data.get('lat', instance.lat)
        instance.lng = validated_data.get('lng', instance.lng)
        instance.banner=validated_data.get('banner',instance.banner)
        instance.logo=validated_data.get('logo',instance.logo)
        instance.short_description = validated_data.get('short_description', instance.short_description)
        instance.long_description = validated_data.get('long_description', instance.long_description)
        if validated_data.get('website_link', instance.website_link) is not None:
            instance.website_link = validated_data.get('website_link', instance.website_link)
        if validated_data.get('facebook_link', instance.facebook_link) is not None:
            instance.facebook_link = validated_data.get('facebook_link', instance.facebook_link)
        if validated_data.get('instagram_link', instance.instagram_link) is not None:
            instance.instagram_link = validated_data.get('instagram_link', instance.instagram_link)

        # Update amenities if provided
        if 'amenities' in validated_data:
            instance.amenities = validated_data.get('amenities', instance.amenities)
        
        # Save the updated instance
        instance.save()
        return instance
    

###################################Gallery#######################################
class SaloonGallerySerializer(serializers.ModelSerializer):
    images = serializers.ImageField(required=True)

    class Meta:
        model = Gallery
        fields = ['id', 'images']

    def create(self, validated_data):
        # Ensure the image is saved
        return Gallery.objects.create(**validated_data)

    def get_images(self, obj):
        if obj.images and hasattr(obj.images, 'url'):
            request = self.context.get('request')
            # Return absolute URL if request is provided
            return request.build_absolute_uri(obj.images.url) if request else obj.images.url
        return None
    def update(self, instance, validated_data):
        instance.images = validated_data.get('images', instance.images)
        instance.save()
        return instance
    
##########################Services###########################

class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImage
        fields = ['id', 'image']

class ServiceVariationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceVariationImage
        fields = ['id', 'image']

class ServiceVariationInfoSerializer(serializers.ModelSerializer):
    price=serializers.SerializerMethodField()
    class Meta:
        model = ServiceVariation
        fields = ['id', 'name','duration', 'price']
    def get_price(self, obj):
        if obj.discount_price:
            return obj.discount_price
        else:
            return obj.price

class ServiceVariationSerializer(serializers.ModelSerializer):
    images = ServiceVariationImageSerializer(many=True, read_only=True)

    currency= serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ServiceVariation
        fields = ['id', 'name', 'description', 'duration', 'price', 'discount_price', 'images','currency']

    def get_currency(self, obj):
        return obj.service.saloon.currency.symbol
    def create(self, validated_data):
        variation = ServiceVariation.objects.create(**validated_data)

        return variation
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.price = validated_data.get('price', instance.price)
        instance.discount_price = validated_data.get('discount_price', instance.discount_price)
        instance.save()
        return instance

class ServiceSerializer(serializers.ModelSerializer):
    # images = ServiceImageSerializer(many=True, required=False)
    logo=serializers.SerializerMethodField(read_only=True)
    variations = ServiceVariationSerializer(many=True, required=False)
    logo=serializers.SerializerMethodField(read_only=True)
    icon=serializers.ImageField(required=True)

    class Meta:
        model = Service
        fields = ['id', 'name','logo', 'variations','icon']

    def get_logo(self, obj):
        if obj.saloon and obj.saloon.logo:
            return obj.saloon.logo.url
        return None

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        # variations_data = validated_data.pop('variations', [])
        service = Service.objects.create(**validated_data)

        # Save service images
        for image_data in images_data:
            ServiceImage.objects.create(service=service, **image_data)

        # Save service variations
        # for variation_data in variations_data:
        #     images = variation_data.pop('images', [])
        #     variation = ServiceVariation.objects.create(service=service, **variation_data)

        #     # Save variation images
        #     for image_data in images:
        #         ServiceVariationImage.objects.create(variation=variation, **image_data)

        return service

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        # variations_data = validated_data.pop('variations', [])

        # Update basic service fields
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.min_duration = validated_data.get('min_duration', instance.min_duration)
        instance.max_duration = validated_data.get('max_duration', instance.max_duration)
        instance.icon=validated_data.get('icon', instance.icon)
        instance.save()
        instance.images.all().delete()
        for image_data in images_data:
            ServiceImage.objects.create(service=instance, **image_data)
        # instance.variations.all().delete()
        # for variation_data in variations_data:
        #     images = variation_data.pop('images', [])
        #     variation = ServiceVariation.objects.create(service=instance, **variation_data)
        #     for image_data in images:
        #         ServiceVariationImage.objects.create(variation=variation, **image_data)

        return instance
    
########################################################Staffs##########################################################################
class WorkingDaySerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkingDay
        fields = ['id','day_of_week', 'start_time', 'end_time','is_working']

    

    def create(self, validated_data):
        working_day = WorkingDay.objects.create(**validated_data)
        return working_day
    

    def update(self, instance, validated_data):
        instance.staff = validated_data.get('staff', instance.staff)
        instance.day_of_week = validated_data.get('day_of_week', instance.day_of_week)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.is_working = validated_data.get('is_working', instance.is_working)
        instance.save()
        return instance

class ServicesInfoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()

class StaffInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['name','image']

class StaffSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    contact_no = serializers.CharField(max_length=255, required=True)
    image = serializers.ImageField(required=False)
    services = ServicesInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'saloon', 'services', 'name', 'email', 'contact_no', 'image','buffer_time']

    def create(self, validated_data):
        # Create the Staff object
        staff = Staff.objects.create(**validated_data)

        return staff

    def update(self, instance, validated_data):
        services_data = validated_data.pop('services', None)
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.contact_no = validated_data.get('contact_no', instance.contact_no)
        instance.image = validated_data.get('image', instance.image)
        instance.buffer_time = validated_data.get('buffer_time', instance.buffer_time)
        instance.save()
        if services_data is not None:
            instance.services.set(services_data)

        return instance

#################################################Appointments and Appointment Slots##################################################
class AppointmentSlotByStaffSerializer(serializers.ModelSerializer):
    end_time = serializers.TimeField(read_only=True)
    working_day = serializers.PrimaryKeyRelatedField(queryset=WorkingDay.objects.all(), required=True)
    buffer_time = serializers.DurationField(read_only=True)

    class Meta:
        model = AppointmentSlot
        fields = ['id', 'start_time', 'service_variation', 'end_time', 'buffer_time','working_day','buffer_time']


    def update(self, instance, validated_data):
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.service_variation = validated_data.get('service_variation', instance.service_variation)
        instance.buffer_time = validated_data.get('buffer_time', instance.buffer_time)
        instance.working_day = validated_data.get('working_day', instance.working_day)
        instance.save()
        return instance
    
    


    ###########################################Opening Hours############################################################

class OpeningHourSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(required=False)
    end_time = serializers.TimeField(required=False)
    day_of_week = serializers.CharField(required=False)
    class Meta:
        model = OpeningHour
        fields = ('day_of_week', 'start_time', 'end_time', 'is_open')

    def create(self, validated_data):
        opening_hour = OpeningHour.objects.create(**validated_data)
        return opening_hour

    def update(self, instance, validated_data):
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.day_of_week = validated_data.get('day_of_week', instance.day_of_week)
        instance.is_open = validated_data.get('is_open', instance.is_open)
        instance.save()
        return instance
    
    
##################################################Appointments####################################################################

class AppointmentSerializer(serializers.ModelSerializer):
    service_variation = serializers.SerializerMethodField()
    class Meta:
        model = Appointment
        fields = ['id','appointment_id','user', 'service_variation', 'start_time', 'end_time', 'fullname','phone_number','date','total_price']
    def get_service_variation(self, obj):
        service_variations = ServiceVariation.objects.filter(id__in=obj.service_variation.all())
        return ServiceVariationInfoSerializer(service_variations, many=True).data

##########################################ApointmentDetails####################################################################
class AppointmentDetailsSerializer(serializers.ModelSerializer):
    service_variation = serializers.SerializerMethodField()
    service=ServicesInfoSerializer()
    staff=StaffInfoSerializer()
    user=serializers.SerializerMethodField()
    class Meta:
        model = Appointment
        fields = ['id','appointment_id','user','staff','service_variation','service', 'start_time', 'end_time', 'fullname','currency','email','phone_number','date','total_price','status','payment_status','payment_method','created_at']
    def get_service_variation(self, obj):
        service_variations = ServiceVariation.objects.filter(id__in=obj.service_variation.all())
        return ServiceVariationInfoSerializer(service_variations, many=True).data
    
    def get_user(self, obj):
        user = obj.user
        return f"{user.first_name} {user.last_name}" if user else "Unknown"

####################################Offers#####################################################

class SaloonOffersSerializer(serializers.ModelSerializer):
    is_active=serializers.SerializerMethodField
    class Meta:
        model = SaloonOffers
        fields = ['id', 'name', 'description', 'percentage_discount','fixed_discount', 'start_offer', 'end_offer', 'is_active']
        read_only_fields = ['id','is_active']

    def get_is_active(self, obj):
        """Return True if the current time is within the offer's active period."""
        now = datetime.now()
        return obj.start_offer <= now <= obj.end_offer
    def create(self, validated_data):
        offer = SaloonOffers.objects.create(**validated_data)
        return offer

class SaloonOfferDetailsSerializer(serializers.ModelSerializer):
    is_active=serializers.SerializerMethodField
    class Meta:
        model = SaloonOffers
        fields = ['id', 'name', 'description', 'percentage_discount','fixed_discount', 'start_offer', 'end_offer', 'is_active']
        read_only_fields = ['id','is_active']

    def get_is_active(self, obj):
        """Return True if the current time is within the offer's active period."""
        now = datetime.now()
        return obj.start_offer <= now <= obj.end_offer
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.percentage_discount = validated_data.get('percentage_discount', instance.percentage_discount)
        instance.fixed_discount = validated_data.get('fixed_discount', instance.fixed_discount)
        instance.start_offer = validated_data.get('start_date', instance.start_offer)
        instance.end_offer = validated_data.get('end_date', instance.end_offer)
        instance.save()
        return instance

########################SaloonCoupons#######################################

class SaloonCouponsSerializer(serializers.ModelSerializer):
    is_active=serializers.SerializerMethodField
    class Meta:
        model = SaloonCoupons
        fields = ['id','code', 'percentage_discount','fixed_discount', 'start_date', 'end_date', 'is_active','services','is_global']
        read_only_fields = ['id','is_active']

    def get_is_active(self, obj):
        """Return True if the current time is within the offer's active period."""
        if not obj.start_date or not obj.end_date:
            return False
        else:
            now = datetime.now()
            return obj.start_date <= now <= obj.end_date
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        percentage_discount = data.get('percentage_discount')
        fixed_discount = data.get('fixed_discount')
        services = data.get('services')
        is_global = data.get('is_global')
        if end_date < start_date:
            raise serializers.ValidationError("End date cannot be before start date.")
        if percentage_discount and fixed_discount:
            raise serializers.ValidationError("Only one of 'percentage_discount' or 'fixed_discount' can be selected.")
        if services and is_global:
            raise serializers.ValidationError("A coupon cannot be both global and specific to services.")
        return data
    
    def create(self, validated_data):
    # Retrieve saloon_id from the request context
        saloon_id = self.context['request'].parser_context['kwargs'].get('saloon_id')
        if not saloon_id:
            raise serializers.ValidationError({"saloon": "Saloon ID is required."})

        # Fetch the saloon instance
        try:
            saloon = Saloon.objects.get(id=saloon_id)
        except Saloon.DoesNotExist:
            raise serializers.ValidationError({"saloon": "Invalid saloon ID."})

        # Remove services from validated data to set it later
        service_ids = validated_data.pop('services', [])
        
        # Create the coupon
        coupon = SaloonCoupons.objects.create(saloon=saloon, **validated_data)
        
        # Associate services
        if service_ids:
            coupon.services.set(service_ids)
        
        return coupon
    
class SaloonCouponListSerializer(serializers.ModelSerializer):
    discount_type = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()

    class Meta:
        model = SaloonCoupons
        fields = ['id','code', 'percentage_discount', 'fixed_discount', 'start_date', 'end_date', 'is_active', 'is_global','discount_type','services']
    
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
    def get_services(self, obj):
        return [{"id": str(service.id), "name": service.name} for service in obj.services.all()]

    

class SaloonCouponsDetailsSerializer(serializers.ModelSerializer):
    is_active=serializers.SerializerMethodField
    class Meta:
        model = SaloonCoupons
        fields = ['id', 'name', 'description','services', 'code', 'percentage_discount','fixed_discount', 'start_date', 'end_date', 'is_active', 'is_global']
        read_only_fields = ['id','is_active']

    def get_is_active(self, obj):
        """Return True if the current time is within the offer's active period."""
        now = datetime.now()
        return obj.start_date <= now <= obj.end_date
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        percentage_discount = data.get('percentage_discount')
        fixed_discount = data.get('fixed_discount')
        services = data.get('services')
        is_global = data.get('is_global')
        if end_date < start_date:
            raise serializers.ValidationError("End date cannot be before start date.")
        if percentage_discount and fixed_discount:
            raise serializers.ValidationError("Only one of 'percentage_discount' or 'fixed_discount' can be selected.")
        if services and is_global:
            raise serializers.ValidationError("A coupon cannot be both global and specific to services.")
        return data
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.code = validated_data.get('code', instance.code)
        instance.percentage_discount = validated_data.get('percentage_discount', instance.percentage_discount)
        instance.fixed_discount = validated_data.get('fixed_discount', instance.fixed_discount)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.is_global = validated_data.get('is_global', instance.is_global)
        instance.save()
        return instance
    
 