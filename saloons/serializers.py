from rest_framework import serializers
from saloons.models import Saloon,Gallery
from review.serializers import ReviewSerializer
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz
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
        if not obj.is_open:
            return False
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=self.lat, lng=self.lng)
        if not timezone_str:
            raise ValueError("Could not determine timezone for the saloon location")

        local_timezone = pytz.timezone(timezone_str)
        local_now = datetime.now(local_timezone)
        current_day = local_now.strftime('%A')

        opening_hours = OpeningHour.objects.filter(day__day_name=current_day).first()

        if not opening_hours or not opening_hours.is_open:
            return False

        return opening_hours.from_time <= local_now.time() <= opening_hours.to_time
    
    
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
    amenities = serializers.SerializerMethodField()
    class Meta:
        model = Saloon
        fields = ['id','name','logo','short_description','long_description','address','banner','email','contact_no','website_link','facebook_link','instagram_link','lat','lng','is_open','amenities']

        depth = 1

    def get_amenities(self, obj):
        return obj.amenities.all()

    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None 
    def get_is_open(self, obj):
        if not obj.is_open:
            return False
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=self.lat, lng=self.lng)
        if not timezone_str:
            raise ValueError("Could not determine timezone for the saloon location")

        local_timezone = pytz.timezone(timezone_str)
        local_now = datetime.now(local_timezone)
        current_day = local_now.strftime('%A')

        opening_hours = OpeningHour.objects.filter(day__day_name=current_day).first()

        if not opening_hours or not opening_hours.is_open:
            return False

        return opening_hours.from_time <= local_now.time() <= opening_hours.to_time
 
        