from rest_framework import serializers
from openinghours.models import OpeningHour

class OpeningHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHour
        fields = ['saloon', 'day_of_week', 'start_time', 'end_time','is_open']