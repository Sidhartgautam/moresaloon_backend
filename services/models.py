from django.db import models
import uuid
from saloons.models import Saloon
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    saloon = models.ForeignKey(Saloon, related_name='services', on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    min_duration = models.DurationField(help_text="Base duration of the service (e.g., 1 hour, 30 minutes)", null=True, blank=True)
    max_duration = models.DurationField(help_text="Maximum duration of the service based on variations", null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    def update_durations(self):
        variations = self.variations.all()
        if variations.exists():
            durations = [variation.duration for variation in variations]
            self.min_duration = min(durations)
            self.max_duration = max(durations)
            self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    class Meta:
        unique_together = ('saloon', 'name') 

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
        return f"Image for {self.service.name}-{self.service.saloon.name}"


class ServiceVariation(models.Model):
    id =models.UUIDField(primary_key=True,default=uuid.uuid4 ,editable=False)
    service =models.ForeignKey(Service,on_delete=models.CASCADE,related_name="variations")
    description =models.TextField(null=True, blank=True,help_text="Description of the service variation")
    name =models.CharField(max_length=255)
    duration =models.DurationField(help_text="Duration of the service (e.g., 1 hour, 30 minutes)")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Additional price for this variation",null=True, blank=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Discounted price for this variation",null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.service.name}"
    def get_price(self):
        if self.discount_price>0:
            return self.discount_price
        return self.price
    
    def get_dis_price(self):
        if self.discount_price:
            return self.price
        return None
    
class ServiceVariationImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variation = models.ForeignKey(ServiceVariation, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='services/service_variations/images')

    def __str__(self):
        return f"Image for {self.variation.name}-{self.variation.service.saloon.name}"

