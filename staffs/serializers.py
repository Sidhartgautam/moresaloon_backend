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
    working_days = WorkingDaySerializer(many=True, required=False)
    saloon = serializers.PrimaryKeyRelatedField(queryset=Saloon.objects.all())

    class Meta:
        model = Staff
        fields = ['id','saloon', 'name', 'position', 'working_days']
