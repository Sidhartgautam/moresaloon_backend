from rest_framework import serializers
from .models import Appointment
from staffs.models import Staff

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['user', 'saloon', 'service', 'staff', 'date', 'start_time', 'end_time', 'status', 'payment_status', 'payment_method']

    def validate(self, data):
        # Ensure the appointment is within staff working hours and doesn't overlap with breaks
        staff = data['staff']
        date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']

        working_day = staff.working_days.filter(day_of_week=date.strftime('%A')).first()

        if not working_day:
            raise serializers.ValidationError(f"Staff is not working on {date.strftime('%A')}.")

        # Check if the appointment time falls within the working hours
        if not (working_day.start_time <= start_time and end_time <= working_day.end_time):
            raise serializers.ValidationError("Appointment time is outside of staff working hours.")

        # Check for overlaps with break times
        for break_time in working_day.break_times.all():
            if break_time.break_start < end_time and start_time < break_time.break_end:
                raise serializers.ValidationError("Appointment time overlaps with staff break time.")

        # Check for overlapping appointments for the same staff
        overlapping_appointments = Appointment.objects.filter(
            staff=staff,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if overlapping_appointments:
            raise serializers.ValidationError("This staff member already has an appointment at this time.")

        return data
