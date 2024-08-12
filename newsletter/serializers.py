from rest_framework import serializers
from .models import Newsletter

class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ('email',)
        
    def validate(self, attrs):
        newletter = Newsletter.objects.filter(email=attrs['email']).exists()
        if newletter:
            raise serializers.ValidationError('Email already exists')
        return super().validate(attrs)