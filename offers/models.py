from django.db import models
from services.models import ServiceVariation
from saloons.models import Saloon
import uuid

class SaloonOffer(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=255)
    service_variation = models.ManyToManyField(ServiceVariation)
    banner = models.ImageField(upload_to="saloon_offers/", null=True)
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE, null=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price of selected service variations", blank=True, null=True)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Offer price after discount", blank=True, null=True)
    description = models.CharField(max_length=255, null=True)
    start_offer = models.DateTimeField(auto_now=True)
    end_offer = models.DateTimeField()

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     if self.service_variation.exists():
    #         self.original_price = sum(variation.price for variation in self.service_variation.all())
    #     super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.original_price = sum(variation.price for variation in self.service_variation.all())
        super().save(*args, **kwargs)
