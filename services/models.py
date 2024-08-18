from django.db import models
import uuid
from saloons.models import Saloon
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class ServiceCategory(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=255)
    saloon = models.ForeignKey(Saloon, related_name='service_categories', on_delete=models.CASCADE,null=True)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.saloon.name}"
    class Meta:
        unique_together = ('saloon', 'name') 

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
    base_duration = models.DurationField(help_text="Duration of the service (e.g., 1 hour, 30 minutes)")
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
        return f"Image for {self.service.name}-{self.service.saloon.name}"


class ServiceVariation(models.Model):
    id =models.UUIDField(primary_key=True,default=uuid.uuid4 ,editable=False)
    service =models.ForeignKey(Service,on_delete=models.CASCADE,related_name="variations")
    name =models.CharField(max_length=255)
    additional_duration =models.DurationField(help_text="Duration of the service (e.g., 1 hour, 30 minutes)")
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Additional price for this variation",null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.service.name}"

    @property
    def total_duration(self):
        return self.service.base_duration + self.additional_duration    

    @property
    def total_price(self):
        return self.service.price + self.additional_price    
