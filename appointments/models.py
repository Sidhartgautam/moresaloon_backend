from django.db import models
from saloons.models import Saloon
from services.models import Service
from users.models import User
from staffs.models import Staff
import uuid
from django.core.exceptions import ValidationError
from datetime import timedelta, datetime, date

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

class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_id = models.CharField(max_length=50, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
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
        if not working_day or not (working_day.start_time <= self.start_time < working_day.end_time):
            raise ValidationError("The selected time is outside of the staff's working hours.")

        # Validate that the appointment doesn't overlap with a break
        for break_time in working_day.break_times.all():
            if break_time.break_start < self.end_time and break_time.break_end > self.start_time:
                raise ValidationError("The appointment time overlaps with a break.")

    def save(self, *args, **kwargs):
        # Calculate end_time based on service duration
        if self.start_time and self.service:
            service_duration = self.service.duration
            start_datetime = datetime.combine(date.today(), self.start_time)
            end_datetime = start_datetime + service_duration
            self.end_time = end_datetime.time()
        self.clean()
        super().save(*args, **kwargs)
