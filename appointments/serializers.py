from datetime import datetime, timedelta
from rest_framework import serializers
from services.models import Service, ServiceVariation
from .models import AppointmentSlot, Appointment
from staffs.models import WorkingDay, BreakTime

class AppointmentSlotSerializer(serializers.ModelSerializer):
    end_time = serializers.TimeField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True) 
    buffer_time = serializers.DurationField(default=timedelta(minutes=10))
    class Meta:
        model = AppointmentSlot
        fields = ['id', 'saloon', 'staff', 'date', 'start_time', 'end_time', 'is_available', 'service', 'service_variation', 'buffer_time', 'total_price']

    def validate(self, data):
        # Extract the relevant fields
        staff = data.get('staff')
        date = data.get('date')
        start_time = data.get('start_time')
        service = data.get('service')
        service_variation = data.get('service_variation')
        buffer_time = data.get('buffer_time', timedelta(minutes=10))  # Default to 10 minutes if not provided

        if not staff.services.filter(id=service.id).exists():
            raise serializers.ValidationError("The selected staff member does not provide this service.")

        # Ensure that staff, date, and start_time are provided
        if not all([staff, date, start_time]):
            raise serializers.ValidationError("Staff, date, and start time are required.")
        
        # Ensure that either service or service_variation is provided
        if not service and not service_variation:
            raise serializers.ValidationError("Either service or service variation must be provided.")

        # Calculate end_time based on service or service_variation
        if service_variation:
            service_duration = service_variation.total_duration
        elif service:
            service_duration = service.base_duration

        start_datetime = datetime.combine(date, start_time)
        end_datetime = start_datetime + service_duration
        end_time = end_datetime.time()

        # Add buffer_time to end time
        end_datetime += buffer_time
        end_time = end_datetime.time()
        
        # Check for overlapping appointment slots
        overlapping_slots = AppointmentSlot.objects.filter(
            staff=staff,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(pk=self.instance.pk if self.instance else None).exists()

        if overlapping_slots:
            raise serializers.ValidationError("The selected time slot overlaps with another appointment slot.")

        # Check if this booking pushes into the next available slot
        next_slot = AppointmentSlot.objects.filter(
            staff=staff,
            date=date,
            start_time__gte=end_time
        ).exclude(pk=self.instance.pk if self.instance else None).order_by('start_time').first()

        if next_slot and end_time > next_slot.start_time:
            raise serializers.ValidationError("This booking extends into the next available slot for this staff member.")
        
        # Check staff availability on the selected date
        staff_working_day = WorkingDay.objects.filter(staff=staff, day_of_week=date.strftime('%A')).first()
        if not staff_working_day:
            raise serializers.ValidationError("The selected staff member is not available on this day.")

        # Check staff’s working hours
        if start_time < staff_working_day.start_time or end_time > staff_working_day.end_time:
            raise serializers.ValidationError("The appointment time falls outside the staff member's working hours.")

        # Check break times
        staff_breaks = BreakTime.objects.filter(working_day=staff_working_day)
        for break_time in staff_breaks:
            if start_time < break_time.break_end and end_time > break_time.break_start:
                raise serializers.ValidationError("The appointment overlaps with the staff member's break time.")

        # Set the calculated end_time
        data['end_time'] = end_time
        
        return data


class AppointmentSerializer(serializers.ModelSerializer):
    # Allow selecting multiple services and service variations
    service = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())
    service_variation = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=ServiceVariation.objects.all())
    end_time = serializers.TimeField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    buffer_time = serializers.DurationField(default=timedelta(minutes=10))  # Include buffer_time

    class Meta:
        model = Appointment
        fields = [
            'user', 
            'saloon', 
            'service', 
            'service_variation', 
            'staff', 
            'date', 
            'start_time',
            'end_time', 
            'status', 
            'payment_status', 
            'payment_method', 
            'total_price', 
            'buffer_time'
        ]

    def validate(self, data):
        staff = data['staff']
        date = data['date']
        start_time = data['start_time']
        services = data['service']
        buffer_time = data.get('buffer_time', timedelta(minutes=10))

        # Ensure the selected staff can provide all the selected services
        for service in services:
            if not staff.services.filter(id=service.id).exists():
                raise serializers.ValidationError(f"The selected staff member does not provide the service: {service.name}")

        # Ensure the staff is working on the selected day
        working_day = staff.working_days.filter(day_of_week=date.strftime('%A')).first()
        if not working_day:
            raise serializers.ValidationError(f"Staff is not working on {date.strftime('%A')}.")

        # Calculate the total duration of services and the end time
        total_duration = sum([service.base_duration for service in services], timedelta())
        end_time = (datetime.combine(date, start_time) + total_duration + buffer_time).time()
        data['end_time'] = end_time

        # Ensure the appointment falls within staff's working hours
        if not (working_day.start_time <= start_time and end_time <= working_day.end_time):
            raise serializers.ValidationError("Appointment time is outside of staff working hours.")

        # Check for overlaps with staff's break times
        for break_time in working_day.break_times.all():
            if break_time.break_start < end_time and start_time < break_time.break_end:
                raise serializers.ValidationError("Appointment time overlaps with staff break time.")

        # Check for overlapping appointments with the same staff
        overlapping_appointments = Appointment.objects.filter(
            staff=staff,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if overlapping_appointments:
            raise serializers.ValidationError("This staff member already has an appointment at this time.")

        # Prevent consecutive day bookings for services requiring recovery time
        previous_appointment = Appointment.objects.filter(
            user=data['user'],
            staff=staff,
            date__lt=date
        ).order_by('-date').first()

        if previous_appointment and (date - previous_appointment.date).days < 1:
            raise serializers.ValidationError("You cannot book appointments on consecutive days for services requiring recovery time.")

        return data

    def create(self, validated_data):
        services = validated_data.pop('service')
        service_variations = validated_data.pop('service_variation', [])

        appointment = Appointment.objects.create(**validated_data)
        appointment.service.set(services)
        appointment.service_variation.set(service_variations)

        # Calculate the total price
        total_price = sum([variation.total_price if variation else service.price for service, variation in zip(services, service_variations)])
        appointment.total_price = total_price
        appointment.save()

        return appointment
    

class AvailableSlotSerializer(serializers.ModelSerializer):
    saloon = serializers.StringRelatedField()
    staff = serializers.StringRelatedField()
    service = serializers.StringRelatedField()

    class Meta:
        model = AppointmentSlot
        fields = ['start_time', 'saloon', 'staff', 'service', 'is_available']


