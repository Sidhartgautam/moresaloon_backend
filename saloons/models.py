from django.db import models
from core.utils.fields import LatitudeField, LongitudeField
import uuid
from country.models import Country,Currency
from taggit.managers import TaggableManager
from django.contrib.postgres.fields import ArrayField

class Saloon(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    currency =models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    logo = models.ImageField(upload_to='saloons/logo')
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True)
    short_description = models.CharField(max_length=255, null=True)
    long_description = models.TextField(null=True)
    lat = LatitudeField()
    lng = LongitudeField()
    banner = models.ImageField(upload_to='saloons/banner', null=True, blank=True)
    email = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=50)
    website_link = models.CharField(max_length=255, null=True, blank=True)
    facebook_link = models.CharField(max_length=255, null=True, blank=True)
    instagram_link = models.CharField(max_length=255, null=True, blank=True)
    amenities = ArrayField(
            models.CharField(max_length=20, blank=True),
            size=20,
            default=list
    )
    is_open= models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Gallery(models.Model):
    id = models.UUIDField( 
        primary_key = True, 
        default = uuid.uuid4, 
        editable = False)
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE)
    images = models.ImageField(upload_to="saloons/gallery")

    def __str__(self):
        return f"Image for {self.saloon.name}"
    
# class FeaturedSaloons(models.Model):
#     id = models.UUIDField(
#         primary_key=True,
#         default=uuid.uuid4,
#         editable=False
#     )
#     saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.saloon.name}"
    