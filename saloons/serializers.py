from rest_framework import serializers
from saloons.models import Saloon,Gallery
from review.serializers import ReviewSerializer
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz
from openinghours.models import OpeningHour
class SaloonSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False)  
    is_open=serializers.SerializerMethodField()
    rating=serializers.SerializerMethodField()
    review_count=serializers.SerializerMethodField()
    class Meta:
        model = Saloon
        fields = ['id','name','logo','address','banner','is_open','rating','review_count']

        depth = 1

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None 
    def get_is_open(self, obj):
        if not obj.is_open:
            return False
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=obj.lat, lng=obj.lng)
        if not timezone_str:
            raise ValueError("Could not determine timezone for the saloon location")

        local_timezone = pytz.timezone(timezone_str)
        local_now = datetime.now(local_timezone)
        current_day = local_now.strftime('%A')

        opening_hours = OpeningHour.objects.filter(day_of_week=current_day).first()

        if not opening_hours or not opening_hours.is_open:
            return False

        return opening_hours.start_time <= local_now.time() <= opening_hours.start_time
    
    
class GallerySerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    class Meta:
        model = Gallery
        fields = ['id','images']
    def get_images(self, obj):
        return obj.images.url

class PopularSaloonSerializer(serializers.ModelSerializer):
    appointments_count = serializers.IntegerField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Saloon
        fields = ['id', 'name', 'logo','short_description','address','appointments_count','review_count','banner']

class SaloonDetailSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False)
    is_open=serializers.SerializerMethodField()
    amenities = serializers.SerializerMethodField()
    class Meta:
        model = Saloon
        fields = ['id','name','logo','short_description','long_description','address','banner','email','contact_no','website_link','facebook_link','instagram_link','lat','lng','is_open','amenities',]

        depth = 1

    def get_amenities(self, obj):
        return obj.amenities


    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None 
    def get_is_open(self, obj):
        if not obj.is_open:
            return False
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=obj.lat, lng=obj.lng)
        if not timezone_str:
            raise ValueError("Could not determine timezone for the saloon location")

        local_timezone = pytz.timezone(timezone_str)
        local_now = datetime.now(local_timezone)
        current_day = local_now.strftime('%A')

        opening_hours = OpeningHour.objects.filter(day_of_week=current_day).first()

        if not opening_hours or not opening_hours.is_open:
            return False

        return opening_hours.start_time <= local_now.time() <= opening_hours.end_time
    

class SaloonListForMoreDealsSerializer(serializers.ModelSerializer):
    open_hrs = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Saloon
        fields = ['id', 'name', 'open_hrs', 'banner', 'address', 'user','slug']

    def get_open_hrs(self, obj):
        return None
    
    def get_user(self, obj):
        return obj.user.username