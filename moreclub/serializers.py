from rest_framework import serializers
from saloons.models import Saloon,Gallery
from country.models import Country,Currency
from staffs.models import Staff, WorkingDay
from services.models import Service, ServiceVariation, ServiceImage, ServiceVariationImage
from services.serializers import ServiceVariationSerializer
from appointments.models import Appointment, AppointmentSlot
from appointments.serializers import AppointmentSlotSerializer
from openinghours.models import OpeningHour
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
        instance.short_description = validated_data.get('short_description', instance.short_description)
        instance.long_description = validated_data.get('long_description', instance.long_description)
        instance.website_link = validated_data.get('website_link', instance.website_link)
        instance.facebook_link = validated_data.get('facebook_link', instance.facebook_link)
        instance.instagram_link = validated_data.get('instagram_link', instance.instagram_link)

        # Update amenities if provided
        if 'amenities' in validated_data:
            instance.amenities = validated_data.get('amenities', instance.amenities)
        
        # Save the updated instance
        instance.save()
        return instance
    

###################################Gallery#######################################
class SaloonGallerySerializer(serializers.ModelSerializer):
    images=serializers.SerializerMethodField()
    class Meta:
        model = Gallery
        fields = ['id', 'images']

    def get_images(self, obj):
        return obj.images.url


    def create(self, validated_data):
        gallery = Gallery.objects.create(**validated_data)
        return gallery
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

    class Meta:
        model = Service
        fields = ['id', 'name','logo', 'variations']

    def get_logo(self, obj):
        if obj.saloon and obj.saloon.logo:
            return obj.saloon.logo.url
        return None

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        variations_data = validated_data.pop('variations', [])
        service = Service.objects.create(**validated_data)

        # Save service images
        for image_data in images_data:
            ServiceImage.objects.create(service=service, **image_data)

        # Save service variations
        for variation_data in variations_data:
            images = variation_data.pop('images', [])
            variation = ServiceVariation.objects.create(service=service, **variation_data)

            # Save variation images
            for image_data in images:
                ServiceVariationImage.objects.create(variation=variation, **image_data)

        return service

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        variations_data = validated_data.pop('variations', [])

        # Update basic service fields
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.min_duration = validated_data.get('min_duration', instance.min_duration)
        instance.max_duration = validated_data.get('max_duration', instance.max_duration)
        instance.save()
        instance.images.all().delete()
        for image_data in images_data:
            ServiceImage.objects.create(service=instance, **image_data)
        instance.variations.all().delete()
        for variation_data in variations_data:
            images = variation_data.pop('images', [])
            variation = ServiceVariation.objects.create(service=instance, **variation_data)
            for image_data in images:
                ServiceVariationImage.objects.create(variation=variation, **image_data)

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

class StaffSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    contact_no = serializers.CharField(max_length=255, required=True)
    image = serializers.ImageField(required=False)
    services = ServicesInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'saloon', 'services', 'name', 'email', 'contact_no', 'image']

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

    # def get_date(self, obj):
    #      return self.date.strftime("%Y-%m-%d")

    # def validate(self, data):
    #     print(data)
    #     start_time = data.get('start_time')
    #     service_variation = data.get('service_variation')
    #     buffer_time = data.get('buffer_time', timedelta(minutes=10))

    #     # service_duration = service_variation.duration
    #     # start_datetime = datetime.combine(datetime.today(), start_time)
    #     # end_datetime = start_datetime + service_duration + (buffer_time or timedelta())
    #     # data['end_time'] = end_datetime.time()

    #     # Check if the new slot overlaps with other existing slots
    #     overlapping_slots = AppointmentSlot.objects.filter(
    #         working_day=data.get('working_day'),
    #         start_time__lt=data['end_time'],
    #         end_time__gt=start_time
    #     ).exclude(pk=self.instance.pk if self.instance else None)

    #     if overlapping_slots.exists():
    #         raise serializers.ValidationError("This time slot overlaps with another slot for this staff member.")

    #     return data

    # def create(self, validated_data):
    #     staff = self.context['staff'] 
    #     service_variation = validated_data['service_variation']
    #     if not staff.services.filter(id=service_variation.service.id).exists():
    #         raise serializers.ValidationError("The selected staff member does not provide this service.")

    #     appointment_slot = AppointmentSlot.objects.create(**validated_data)
    #     return appointment_slot

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
    class Meta:
        model = Appointment
        fields = ['id', 'saloon', 'staff', 'service', 'service_variation', 'start_time', 'end_time', 'status','date']

    def create(self, validated_data):
        appointment = Appointment.objects.create(**validated_data)
        return appointment

    def update(self, instance, validated_data):
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

##########################################StaffAvailability####################################################################