from django.db import models
import uuid
from saloons.models import Saloon
from django.utils.text import slugify
from core.utils.compression_image import compress_image
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
    icon = models.ImageField(upload_to='service_icons/', null=True, blank=True, help_text="Upload an icon for this service")
    created_at = models.DateTimeField(auto_now_add=True,null=True)  
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def update_durations(self):
        variations = self.variations.all()
        if variations.exists():
            durations = [variation.duration for variation in variations]
            self.min_duration = min(durations)
            self.max_duration = max(durations)
            self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while self.__class__.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        if self.icon and hasattr(self.icon, 'file'):
            self.icon = compress_image(self.icon.file)


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
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.service.update_durations() 

    def delete(self, *args, **kwargs):
        service = self.service
        super().delete(*args, **kwargs)
        service.update_durations()
    
class ServiceVariationImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variation = models.ForeignKey(ServiceVariation, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='services/service_variations')

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file'):
            self.image = compress_image(self.image.file)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.variation.name}-{self.variation.service.saloon.name}"

