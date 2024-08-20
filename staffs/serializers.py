from rest_framework import serializers
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

class StaffSerializer(serializers.ModelSerializer):
    # working_days = WorkingDaySerializer(many=True, required=False)
    saloon = serializers.PrimaryKeyRelatedField(queryset=Saloon.objects.all())
    image = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = ['id','saloon', 'name', 'position', 'image', 'description','email']

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

    class Meta:
        model = Staff
        fields = ['id', 'name', 'image']

    def get_image(self, obj):
        image = obj.image.url if obj.image else None
        return image