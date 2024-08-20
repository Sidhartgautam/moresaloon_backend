from django.db import models
from saloons.models import Saloon
from services.models import Service
from users.models import User
from staffs.models import Staff
import uuid
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

APPOINTMENT_STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled'),
    ('No Show', 'No Show'),
]

PAYMENT_STATUS_CHOICES = [
    ('Unpaid', 'Unpaid'),
    ('Paid', 'Paid'),
]

PAYMENT_METHOD_CHOICES = [
    ('coa', 'Cash on arrival'),
    ('stripe', 'Stripe'),
    ('moredeals', 'MoreDeals')
]



class AppointmentSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE,null=True, blank=True)
    service_variation = models.ForeignKey('services.ServiceVariation', on_delete=models.CASCADE,null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    buffer_time = models.DurationField(default=timedelta(minutes=10),null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.saloon} - {self.staff} - {self.date} {self.start_time} - {self.end_time}"
    def clean(self):
        """
        Custom validation to check for overlapping appointment slots.
        """
        if self.start_time and self.end_time:
            start_datetime = datetime.combine(self.date, self.start_time)
            end_datetime = datetime.combine(self.date, self.end_time)
            overlapping_slots = AppointmentSlot.objects.filter(
                staff=self.staff,
                date=self.date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            ).exclude(pk=self.pk)

            if overlapping_slots.exists():
                raise ValidationError("The selected time slot overlaps with an existing appointment slot for this staff member.")
        super().clean() 

    def save(self, *args, **kwargs):
        if self.start_time and (self.service_variation or self.service):
            start_datetime = datetime.combine(self.date, self.start_time)

            if self.service_variation:
                service_duration = self.service_variation.total_duration
            else:
                service_duration = self.service.base_duration
            end_datetime = start_datetime + service_duration
            self.end_time = end_datetime.time()
        
        if self.service_variation:
            self.total_price = self.service_variation.total_price
        else:
            self.total_price = self.service.price
        self.clean()
        super().save(*args, **kwargs)
    
class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_id = models.CharField(max_length=50, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_variation = models.ForeignKey('services.ServiceVariation', on_delete=models.CASCADE,null=True, blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    buffer_time = models.DurationField(default=timedelta(minutes=10), null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Unpaid')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='coa')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.appointment_id}-{self.user} - {self.saloon} - {self.service} on {self.date} at {self.start_time}"

    def clean(self):
        # Ensure the service and staff are from the same saloon as the appointment
        if self.service.saloon != self.saloon:
            raise ValidationError("The service must be from the same saloon as the appointment.")
        if self.staff.saloon != self.saloon:
            raise ValidationError("The staff must be from the same saloon as the appointment.")
        
        # Validate that the appointment doesn't overlap with another appointment for the same staff
        if self.start_time and self.end_time:  # Ensure both start_time and end_time are not None
            overlapping_appointments = Appointment.objects.filter(
                staff=self.staff,
                date=self.date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            ).exists()

            if overlapping_appointments:
                raise ValidationError("This staff is already booked for the selected time slot.")

        # Validate that the appointment falls within the staff's working hours
        working_day = self.staff.working_days.filter(day_of_week=self.date.strftime('%A')).first()
        if working_day and self.start_time and self.end_time:
            if not (working_day.start_time <= self.start_time < working_day.end_time):
                raise ValidationError("The selected time is outside of the staff's working hours.")

            # Validate that the appointment doesn't overlap with a break
            for break_time in working_day.break_times.all():
                if break_time.break_start and break_time.break_end:  # Ensure break_start and break_end are not None
                    if break_time.break_start < self.end_time and break_time.break_end > self.start_time:
                        raise ValidationError("The appointment time overlaps with a break.")

    def save(self, *args, **kwargs):
        # Calculate end_time based on service variation duration if provided, else use base service duration
        if self.start_time and self.service_variation:
            service_duration = self.service_variation.total_duration
            start_datetime = datetime.combine(self.date, self.start_time)
            end_datetime = start_datetime + service_duration
            self.end_time = end_datetime.time()
        elif self.start_time and self.service and not self.end_time:
            service_duration = self.service.base_duration
            start_datetime = datetime.combine(self.date, self.start_time)
            end_datetime = start_datetime + service_duration
            self.end_time = end_datetime.time()

        # Calculate total price based on service or service variation price
        if self.service_variation:
            self.total_price = self.service_variation.price
        elif self.service:
            self.total_price = self.service.price

        super().save(*args, **kwargs)