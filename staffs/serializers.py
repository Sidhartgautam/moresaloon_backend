from rest_framework import serializers
from services.models import Service
from .models import Staff, WorkingDay, BreakTime
from saloons.models import Saloon

class BreakTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakTime
        fields = ['break_start', 'break_end']

class WorkingDaySerializer(serializers.ModelSerializer):
    break_times = BreakTimeSerializer(many=True, required=False)

    class Meta:
        model = WorkingDay
        fields = ['day_of_week', 'start_time', 'end_time', 'break_times']
    
    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError('Start time must be before end time.')
        return data
    
    

class StaffSerializer(serializers.ModelSerializer):
    saloon = serializers.PrimaryKeyRelatedField(queryset=Saloon.objects.all())
    image = serializers.SerializerMethodField()
    services = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())

    class Meta:
        model = Staff
        fields = ['id','saloon', 'name', 'services', 'image', 'description','email']

    def get_image(self, obj):
        image = obj.image.url if obj.image else None
        return image

class StaffAvailabilitySerializer(serializers.Serializer):
    staff_id = serializers.UUIDField(required=True)
    appointment_date = serializers.DateField(required=True)
    start_time = serializers.TimeField(required=True)
    end_time = serializers.TimeField(required=True)

class StaffListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    appointment_slot_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'name', 'image', 'appointment_slot_count']

    def get_image(self, obj):
        image = obj.image.url if obj.image else None
        return image