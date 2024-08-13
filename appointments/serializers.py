from datetime import datetime, timedelta
from rest_framework import serializers
from .models import Appointment, AppointmentSlot


class AppointmentSlotSerializer(serializers.ModelSerializer):
    end_time = serializers.TimeField(read_only=True)
    class Meta:
        model = AppointmentSlot
        fields = ['id', 'saloon', 'staff', 'date', 'start_time', 'end_time', 'is_available']

class AppointmentSerializer(serializers.ModelSerializer):
    end_time = serializers.TimeField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Appointment
        fields = ['user', 'saloon', 'service', 'staff', 'date', 'start_time','end_time', 'status', 'payment_status', 'payment_method', 'total_price']

    def validate(self, data):
        staff = data['staff']
        date = data['date']
        start_time = data['start_time']
        service = data['service']

        # Ensure the staff is working on the given day
        working_day = staff.working_days.filter(day_of_week=date.strftime('%A')).first()
        if not working_day:
            raise serializers.ValidationError(f"Staff is not working on {date.strftime('%A')}.")

        # Calculate the end time based on service duration
        if start_time and service and service.duration:
            end_time = (datetime.combine(date.today(), start_time) + service.duration).time()
            data['end_time'] = end_time
        else:
            raise serializers.ValidationError("Start time, service, or service duration is missing.")

        # Check if the appointment falls within working hours
        if not (working_day.start_time <= start_time and end_time <= working_day.end_time):
            raise serializers.ValidationError("Appointment time is outside of staff working hours.")

        # Check for overlaps with break times
        for break_time in working_day.break_times.all():
            if break_time.break_start < end_time and start_time < break_time.break_end:
                raise serializers.ValidationError("Appointment time overlaps with staff break time.")

        # Check for overlapping appointments
        overlapping_appointments = Appointment.objects.filter(
            staff=staff,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if overlapping_appointments:
            raise serializers.ValidationError("This staff member already has an appointment at this time.")

        return data
