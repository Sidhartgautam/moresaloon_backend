from django.db import models
from saloons.models import Saloon
from services.models import Service
from users.models import User
from staffs.models import Staff, WorkingDay
from offers.models import SaloonCoupons
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
    working_day = models.ForeignKey(WorkingDay, on_delete=models.CASCADE,null=True, blank=True)
    service_variation = models.ForeignKey('services.ServiceVariation', on_delete=models.CASCADE,null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True)
    buffer_time = models.DurationField(default=timedelta(minutes=10),null=True, blank=True)

    def __str__(self):
        return f"{self.saloon} - {self.staff} -{self.working_day} {self.start_time} - {self.end_time}"
    def clean(self):
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError("End time must be after start time.")
            
            overlapping_slots = AppointmentSlot.objects.filter(
                staff=self.staff,
                working_day=self.working_day,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            ).exclude(pk=self.pk)


            if overlapping_slots.filter(working_day=self.working_day).exists():
             raise ValidationError("The selected time slot overlaps with an existing appointment slot for this staff member.")


        super().clean()

    def save(self, *args, **kwargs):
        if self.start_time and self.service_variation:
            start_datetime = datetime.combine( datetime.today(),self.start_time)
            end_datetime = start_datetime + self.service_variation.duration + (self.buffer_time or timedelta())
            self.end_time = end_datetime.time()
        
        self.clean()
        super().save(*args, **kwargs)
    
class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency=models.ForeignKey('country.Currency',on_delete=models.CASCADE,null=True,blank=True)
    appointment_id = models.CharField(max_length=50, null=True,unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE,null=True, blank=True)
    appointment_slot = models.ForeignKey(AppointmentSlot, on_delete=models.CASCADE, null=True)
    service_variation = models.ManyToManyField('services.ServiceVariation', related_name='appointments',null=True, blank=True)
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
    fullname= models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True) 
    coupon= models.ForeignKey(SaloonCoupons, on_delete=models.CASCADE, null=True, blank=True)
    phone_number= models.CharField(max_length=20, null=True, blank=True)
    note =models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.user} - {self.saloon} - {self.service} on {self.date} at {self.start_time}"
    
    def save(self, *args, **kwargs):
        if self.saloon:
            self.currency = self.saloon.currency
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['staff', 'start_time', 'end_time']),
        ]
        