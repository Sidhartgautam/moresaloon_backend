from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    saloon= serializers.StringRelatedField()
    saloon_id = serializers.SerializerMethodField()
    # image = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['id','user_id','saloon_id','saloon', 'full_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id','saloon', 'user','created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    def get_full_name(self, obj):
        user = obj.user
        return f"{user.first_name} {user.last_name}" if user else "Unknown"
    
    def get_user_id(self, obj):
        user = obj.user
        return user.id if user else None
    def get_saloon_id(self, obj):
        return obj.saloon.id


    # def get_image(self, obj):
    #     return obj.user.profile_image.url

class ReviewCreateSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=True)
    
    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment']