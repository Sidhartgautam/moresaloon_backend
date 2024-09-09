from datetime import datetime, timedelta
from rest_framework import serializers
from saloons.models import Saloon
from staffs.models import Staff
from services.models import Service, ServiceVariation
from .models import AppointmentSlot, Appointment
from staffs.models import WorkingDay, BreakTime
from core.utils.appointment import calculate_total_appointment_price,calculate_appointment_end_time

class AppointmentSlotSerializer(serializers.ModelSerializer):
    end_time = serializers.TimeField(read_only=True)
    price = serializers.SerializerMethodField()
    buffer_time = serializers.DurationField(default=timedelta(minutes=10))
    class Meta:
        model = AppointmentSlot
        fields = ['id', 'saloon', 'staff', 'date', 'start_time', 'end_time', 'is_available', 'service', 'service_variation', 'buffer_time', 'price']

    def get_price(self, obj):
        return obj.service_variation.price
   
    def validate(self, data):
        staff = data.get('staff')
        date = data.get('date')
        start_time = data.get('start_time')
        service = data.get('service')
        service_variation = data.get('service_variation')
        buffer_time = data.get('buffer_time', timedelta(minutes=10)) 

        # Ensure that date is not in the past
        if date and date < datetime.now().date():
            raise serializers.ValidationError("The date cannot be in the past.")

        if not staff.services.filter(id=service.id).exists():
            raise serializers.ValidationError("The selected staff member does not provide this service.")

        # Ensure that staff, date, and start_time are provided
        if not all([staff, date, start_time,service_variation]):
            raise serializers.ValidationError("Staff, date, and start time are required.")
        
        # Ensure that either service or service_variation is provided
        if not service and not service_variation:
            raise serializers.ValidationError("Either service or service variation must be provided.")

        # Calculate end_time based on service or service_variation
        service_duration = service_variation.duration

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


class AppointmentPlaceSerializer(serializers.ModelSerializer):
    service_id = serializers.UUIDField()
    service_variation_ids = serializers.ListField(required=True)
    end_time = serializers.TimeField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    buffer_time = serializers.DurationField(default=timedelta(minutes=10))
    staff_id = serializers.IntegerField() 
    appointment_slot_id = serializers.UUIDField(required=True)
    saloon_id = serializers.UUIDField()
    fullname = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    note = serializers.CharField(required=False)

    class Meta:
        model = Appointment
        fields = [
            'user',
            'saloon_id',
            'service_id',
            'service_variation_ids',
            'staff_id',
            'date',
            'end_time',
            'payment_status',
            'payment_method',
            'total_price',
            'buffer_time',
            'appointment_slot_id',
            'fullname',
            'email',
            'phone_number',
            'note'
        ]

    def validate(self, data):
        staff_id = data['staff_id']
        date = data['date']
        service_id = data['service_id']
        service_variations_ids = data.get('service_variation_ids', [])
        buffer_time = data.get('buffer_time', timedelta(minutes=10))
        slot_id = data.get('appointment_slot_id')

        if date and date < datetime.now().date():
            raise serializers.ValidationError("The date cannot be in the past.")

        # Fetch Staff and Service using IDs
        try:
            staff = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            raise serializers.ValidationError("The selected staff member does not exist.")

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            raise serializers.ValidationError("The selected service does not exist.")

        # Ensure the selected staff can provide the selected service
        if not staff.services.filter(id=service_id).exists():
            raise serializers.ValidationError("The selected staff member does not provide the service.")

        # Ensure the staff is working on the selected day
        working_day = staff.working_days.filter(day_of_week=date.strftime('%A')).first()
        if not working_day:
            raise serializers.ValidationError(f"Staff is not working on {date.strftime('%A')}.")

        # Fetch the appointment slot and use its start_time
        try:
            slot = AppointmentSlot.objects.get(id=slot_id, staff=staff, is_available=True)
            start_time = slot.start_time  # Use the slot's start_time
        except AppointmentSlot.DoesNotExist:
            raise serializers.ValidationError("Invalid or unavailable appointment slot.")

        # Fetch the service variations and calculate total duration
        service_variations = []
        total_duration = timedelta()

        for variation_id in service_variations_ids:
            try:
                variation = ServiceVariation.objects.get(id=variation_id, service=service)
                service_variations.append(variation.id)
            except ServiceVariation.DoesNotExist:
                raise serializers.ValidationError(f"Service variation with ID {variation_id} does not exist or is not valid for the selected service.")

        # Calculate the end time using the utility function
        end_time = calculate_appointment_end_time(date, start_time, service_variations, buffer_time)
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

        return data
    

class AvailableSlotSerializer(serializers.ModelSerializer):
    saloon = serializers.StringRelatedField()
    staff = serializers.StringRelatedField()
    service = serializers.StringRelatedField()

    class Meta:
        model = AppointmentSlot
        fields = ['id','start_time', 'saloon', 'staff', 'service', 'is_available']


class AppointmentListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    saloon = serializers.StringRelatedField()
    service = serializers.StringRelatedField()
    staff = serializers.StringRelatedField()
    service_variation = serializers.StringRelatedField(many=True)
    appointment_slot = serializers.StringRelatedField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    payment_status = serializers.CharField(read_only=True)
    payment_method = serializers.CharField(read_only=True)
    fullname = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    phone_number = serializers.CharField(read_only=True)
    note = serializers.CharField(read_only=True)

    class Meta:
        model = Appointment
        fields = ['user', 'saloon', 'service', 'staff', 'service_variation', 'date', 'start_time', 'end_time', 'appointment_slot','total_price', 'payment_status', 'payment_method', 'fullname', 'email', 'phone_number', 'note']


