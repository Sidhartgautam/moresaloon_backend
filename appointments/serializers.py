from datetime import datetime, timedelta
from rest_framework import serializers
from saloons.models import Saloon
from staffs.models import Staff
from offers.models import SaloonCoupons
from services.models import Service, ServiceVariation
from .models import AppointmentSlot, Appointment
from staffs.models import WorkingDay, BreakTime
from core.utils.appointment import calculate_appointment_end_time

class AppointmentSlotSerializer(serializers.ModelSerializer):
    end_time = serializers.TimeField(read_only=True)
    price = serializers.SerializerMethodField()
    buffer_time = serializers.DurationField(default=timedelta(minutes=10))
    date=serializers.SerializerMethodField()

    class Meta:
        model = AppointmentSlot
        fields = ['id', 'saloon', 'staff','date', 'start_time', 'end_time', 'service', 'service_variation', 'buffer_time', 'price']

    def get_price(self, obj):
        return obj.service_variation.price if obj.service_variation else 0
    
    def get_date(self, obj):
        return obj.date.strftime("%Y-%m-%d")

    def validate(self, data):
        staff = data.get('staff')
        start_time = data.get('start_time')
        service = data.get('service')
        service_variation = data.get('service_variation')
        buffer_time = data.get('buffer_time', timedelta(minutes=10))

        if not staff or not start_time or not service_variation:
            raise serializers.ValidationError("Staff, start time, and service variation are required.")

        if not staff.services.filter(id=service.id).exists():
            raise serializers.ValidationError("The selected staff member does not provide this service.")

        # Calculate end_time based on service_variation duration
        service_duration = service_variation.duration
        start_datetime = datetime.combine(datetime.today(), start_time)  # Use today's date as placeholder
        end_datetime = start_datetime + service_duration + (buffer_time or timedelta())
        end_time = end_datetime.time()

        data['end_time'] = end_time

        # Check for overlapping appointment slots
        overlapping_slots = AppointmentSlot.objects.filter(
            staff=staff,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(pk=self.instance.pk if self.instance else None).exists()

        if overlapping_slots:
            raise serializers.ValidationError("The selected time slot overlaps with another appointment slot.")

        # Check staff availability
        staff_working_day = WorkingDay.objects.filter(staff=staff, day_of_week=datetime.today().strftime('%A')).first()
        if not staff_working_day:
            raise serializers.ValidationError("The selected staff member is not available today.")

        if start_time < staff_working_day.start_time or end_time > staff_working_day.end_time:
            raise serializers.ValidationError("The appointment time falls outside the staff member's working hours.")

        # staff_breaks = BreakTime.objects.filter(working_day=staff_working_day)
        # for break_time in staff_breaks:
        #     if start_time < break_time.break_end and end_time > break_time.break_start:
        #         raise serializers.ValidationError("The appointment overlaps with the staff member's break time.")

        return data

class AppointmentPlaceSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField()
    service_id = serializers.UUIDField()
    service_variation_ids = serializers.ListField(required=True)
    end_time = serializers.TimeField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    buffer_time = serializers.DurationField(read_only=True)
    staff_id = serializers.UUIDField() 
    saloon_id = serializers.UUIDField()
    fullname = serializers.CharField()
    email = serializers.EmailField()
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField()
    note = serializers.CharField(allow_blank=True, allow_null=True)
    currency = serializers.CharField(read_only=True)
    user_send_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    transaction_id = serializers.CharField(read_only=True)
    refferal_points_id = serializers.CharField(read_only=True)
    payment_method_id = serializers.CharField(write_only=True,required=False,allow_blank=True)

    class Meta:
        model = Appointment
        fields = [
            'saloon_id',
            'service_id',
            'service_variation_ids',
            'staff_id',
            'date',
            'start_time',
            'end_time',
            'payment_status',
            'payment_method',
            'payment_method_id',
            'total_price',
            'buffer_time',
            'fullname',
            'email',
            'phone_number',
            'note',
            'currency',
            'coupon_code',
            'user_send_amount',
            'transaction_id',
            'refferal_points_id'
        ]

    def validate(self, data):
        staff_id = data['staff_id']
        saloon_id = data['saloon_id']
        date = data['date']
        start_time = data['start_time']
        service_id = data['service_id']
        service_variations_ids = data.get('service_variation_ids', [])
        coupon_code = data.get('coupon_code')
        # buffer_time = data.get('buffer_time')
        user = self.context['request'].user

        if coupon_code:
            try:
                coupon = SaloonCoupons.objects.get(code=coupon_code, saloon_id=saloon_id)
                if not coupon.is_active():
                    raise serializers.ValidationError({"coupon_code": "This coupon has expired or is inactive."})
                data['coupon'] = coupon
            except SaloonCoupons.DoesNotExist:
                raise serializers.ValidationError({"coupon_code": "Invalid coupon code."})

        saloon = Saloon.objects.get(id=saloon_id)
        if saloon.user == user:
            raise serializers.ValidationError("You cannot book the appointment on your own saloon.")

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
        
        data['buffer_time'] = staff.buffer_time

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
        end_time=calculate_appointment_end_time(date, start_time, service_variations, data['buffer_time'])
        print(end_time)
        data['end_time'] = end_time

        # Ensure the appointment falls within staff's working hours
        if not (working_day.start_time <= working_day.start_time and end_time <= working_day.end_time):
            raise serializers.ValidationError("Appointment time is outside of staff working hours.")

        # Check for overlapping appointments with the same staff
        booked_appointments = Appointment.objects.filter(staff_id=staff_id, date=date)

        for appointment in booked_appointments:
            booked_start = appointment.start_time
            booked_end = appointment.end_time

        # Check for overlap
            if not (end_time <= booked_start or start_time >= booked_end):
                raise serializers.ValidationError("This staff member already has an appointment at this time.")

        return data
    

class AvailableSlotSerializer(serializers.ModelSerializer):
    saloon = serializers.StringRelatedField()
    staff = serializers.StringRelatedField()
    service = serializers.StringRelatedField()
    # service_variation = serializers.ListField()
    class Meta:
        model = AppointmentSlot
        fields = ['id','start_time', 'saloon', 'staff', 'service', 'end_time']


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
    note = serializers.CharField(allow_null=True)

    class Meta:
        model = Appointment
        fields = ['user', 'saloon', 'service', 'staff', 'service_variation', 'date', 'start_time', 'end_time', 'appointment_slot','total_price', 'payment_status', 'payment_method', 'fullname', 'email', 'phone_number', 'note']

class AppointmentServiceVariationListSerializer(serializers.ModelSerializer):
    price=serializers.SerializerMethodField()
    class Meta:
        model = ServiceVariation
        fields = ['id', 'name', 'duration','price']

    def get_price(self, obj):
        if obj.discount_price:
            return obj.discount_price
        else:
            return obj.price
        
class UserAppointmentListSerializer(serializers.ModelSerializer):
    saloon = serializers.StringRelatedField()
    service_variation = AppointmentServiceVariationListSerializer(many=True)
    total_price =serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    date=serializers.DateField()

    class Meta:
        model = Appointment
        fields =['id','saloon','service_variation','start_time','end_time','date','total_price']

    def get_total_price(self, obj):
        return obj.total_price

    def get_start_time(self, obj):
        return obj.start_time
    def get_end_time(self, obj):
        return obj.end_time


