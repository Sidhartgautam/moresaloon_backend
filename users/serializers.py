from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)