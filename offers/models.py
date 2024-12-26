from django.db import models
from services.models import Service
from saloons.models import Saloon
from users.models import User
from django.core.exceptions import ValidationError
import uuid
from django.utils.timezone import now

class SaloonOffers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE, related_name="offers")
    banner = models.ImageField(upload_to="saloon_offers/", null=True)
    percentage_discount = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Percentage discount (e.g., 20 for 20% off)"
    )
    fixed_discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Fixed discount price (e.g., $50 off)"
    )
    description = models.TextField(null=True, blank=True)
    start_offer = models.DateTimeField()
    end_offer = models.DateTimeField()

    def clean(self):
        # Ensure only one discount type is selected
        if self.percentage_discount and self.fixed_discount:
            raise ValidationError("Only one of 'percentage_discount' or 'fixed_discount' can be selected.")
        if not self.percentage_discount and not self.fixed_discount:
            raise ValidationError("One of 'percentage_discount' or 'fixed_discount' must be selected.")
        
    def is_active(self):
        current_time = now()
        return self.start_date <= current_time <= self.end_date

    def __str__(self):
        return f"{self.name} - {self.saloon.name}"
    



class SaloonCoupons(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(
        max_length=50,
        unique=True,
        editable=True,
    )
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE, related_name="coupons")
    services = models.ManyToManyField(Service, blank=True, help_text="Services the coupon applies to.")
    percentage_discount = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Percentage discount (e.g., 20 for 20% off)"
    )
    fixed_discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Fixed discount price (e.g., $50 off)"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_global = models.BooleanField(default=False, help_text="Apply to all services if True")

    def clean(self):
        # Ensure only one discount type is selected
        if self.percentage_discount and self.fixed_discount:
            raise ValidationError("Only one of 'percentage_discount' or 'fixed_discount' can be selected.")
        if not self.percentage_discount and not self.fixed_discount:
            raise ValidationError("One of 'percentage_discount' or 'fixed_discount' must be selected.")
        if self.is_global and self.services.exists():
            raise ValidationError("A coupon cannot be both global and specific to services.")
        
    def is_active(self):
        current_time = now()
        return self.start_date <= current_time <= self.end_date

    def __str__(self):
        return self.code
    
class CouponUsage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(SaloonCoupons, on_delete=models.CASCADE, related_name='usages', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages', null=True, blank=True)
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE, null=True, blank=True, related_name='coupon_usage')
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('coupon', 'user')

    def __str__(self):
        return f"Coupon {self.coupon.code} used by {self.user.username}"