from django.db import models
from services.models import Service
from saloons.models import Saloon
from django.core.exceptions import ValidationError
import uuid

class SaloonOffers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE, related_name="offers")
    banner = models.ImageField(upload_to="saloon_offers/", null=True)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Offer price after discount")
    description = models.TextField(null=True, blank=True)
    start_offer = models.DateTimeField(auto_now=True)
    end_offer = models.DateTimeField()

    def __str__(self):
        return f"{self.name} - {self.saloon.name}"
    

def generate_coupon_code():
    """Generates a unique 8-character alphanumeric coupon code."""
    while True:
        code = uuid.uuid4().hex[:8].upper()
        if not SaloonCoupons.objects.filter(code=code).exists():
            return code


class SaloonCoupons(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(
        max_length=50,
        unique=True,
        default=generate_coupon_code,  
        editable=False,
    )
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE, related_name="coupons")
    services = models.ManyToManyField(Service, blank=True, help_text="Services the coupon applies to.")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_global = models.BooleanField(default=False, help_text="Apply to all services if True")

    def clean(self):
        if self.is_global and self.services.exists():
            raise ValidationError("A coupon cannot be both global and specific to services.")

    def __str__(self):
        return self.code