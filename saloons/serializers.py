from rest_framework import serializers
from saloons.models import Saloon,Gallery,Amenities
from review.serializers import ReviewSerializer
from datetime import datetime
from openinghours.models import OpeningHour
class SaloonSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False)  
    # banner = serializers.ImageField(required=True)
    is_open=serializers.SerializerMethodField()
    class Meta:
        model = Saloon
        fields = ['id','name','logo','address','banner','is_open']

        depth = 1

    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None 
    def get_is_open(self, obj):
        current_time=datetime.now().time()
        current_day=datetime.now().strftime('%A')
        try:
            opening_hours = OpeningHour.objects.filter(saloon=obj, day_of_week=current_day).first()

            if opening_hours and opening_hours.start_time <= current_time <= opening_hours.end_time:
                return "Open"
            return "Closed"
        except OpeningHour.DoesNotExist:
            return "Closed"
    
    
class GallerySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Gallery
        fields = ['id','image']
    def get_image(self, obj):
        return obj.image.url

class PopularSaloonSerializer(serializers.ModelSerializer):
    appointments_count = serializers.IntegerField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Saloon
        fields = ['id', 'name', 'logo','short_description','address','appointments_count','review_count','banner']

class SaloonDetailSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False)
    # banner = serializers.ImageField(required=False)
    # reviews = ReviewSerializer(many=True, read_only=True)
    is_open=serializers.SerializerMethodField()
    class Meta:
        model = Saloon
        fields = ['id','name','logo','short_description','long_description','address','banner','email','contact_no','website_link','facebook_link','instagram_link','lat','lng','is_open']

        depth = 1

    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None 
    def get_is_open(self, obj):
        current_time=datetime.now().time()
        current_day=datetime.now().strftime('%A')
        try:
            opening_hours = OpeningHour.objects.filter(saloon=obj, day_of_week=current_day).first()

            if opening_hours and opening_hours.start_time <= current_time <= opening_hours.end_time:
                return "Open"
            return "Closed"
        except OpeningHour.DoesNotExist:
            return "Closed"
    
class AmenitiesSerializer(serializers.ModelSerializer):
    saloon =serializers.PrimaryKeyRelatedField(queryset=Saloon.objects.all(),required=True)
    class Meta:
        model = Amenities
        fields = ['id','saloon','name']
 
        