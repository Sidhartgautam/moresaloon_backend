from django.db import models
import uuid
from saloons.models import Saloon

class ServiceCategory(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=255)
    saloon = models.ForeignKey(Saloon, related_name='service_categories', on_delete=models.CASCADE,null=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.saloon.name}"

class Service(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    saloon = models.ForeignKey(Saloon, related_name='services', on_delete=models.CASCADE)
    category = models.ForeignKey(ServiceCategory, related_name='services', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    duration = models.DurationField(help_text="Duration of the service (e.g., 1 hour, 30 minutes)")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.saloon.name}"

class ServiceImage(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    service = models.ForeignKey(Service, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='services/images')

    def __str__(self):
        return f"Image for {self.service.name}"
        
