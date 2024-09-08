from rest_framework import serializers
from saloons.models import Saloon,Gallery,Amenities
from review.serializers import ReviewSerializer

class SaloonSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False)
    # banner = serializers.ImageField(required=True)
    class Meta:
        model = Saloon
        fields = ['id','name','logo','address','banner']

        depth = 1

    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None 
    
class GallerySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Gallery
        fields = ('image',)
    def get_image(self, obj):
        return obj.image.url

class PopularSaloonSerializer(serializers.ModelSerializer):
    review_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Saloon
        fields = ('id', 'name', 'logo','short_description','address','review_count')

class SaloonDetailSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False)
    # banner = serializers.ImageField(required=False)
    reviews = ReviewSerializer(many=True, read_only=True)
    class Meta:
        model = Saloon
        fields = ['id','name','logo','short_description','long_description','address','banner','email','contact_no','website_link','facebook_link','instagram_link','reviews','lat','lng']

        depth = 1

    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None 
    
class AmenitiesSerializer(serializers.ModelSerializer):
    saloon =serializers.PrimaryKeyRelatedField(queryset=Saloon.objects.all(),required=True)
    class Meta:
        model = Amenities
        fields = ['id','saloon','name']
 
        