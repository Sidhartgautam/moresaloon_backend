from django.db import models
from services.models import Service
from saloons.models import Saloon
import uuid

class SaloonOffer(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=255)
    service = models.ManyToManyField(Service)
    banner = models.ImageField(upload_to="saloon_offers/", null=True)
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, null=True)
    start_offer = models.DateTimeField(auto_now=True)
    end_offer = models.DateTimeField()

    def __str__(self):
        return self.name



    
