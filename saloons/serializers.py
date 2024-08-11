from rest_framework import serializers
from saloons.models import Saloon,Gallery

class SaloonSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    class Meta:
        model = Saloon
        exclude = ['user']

        depth = 1

    def get_logo(self, obj):
        return obj.logo.url
    
class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ('image',)
        
class UserUploadGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ('image',)

class PopularSaloonSerializer(serializers.ModelSerializer):
    review_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Saloon
        fields = ('id', 'name', 'logo','short_description','address','review_count')