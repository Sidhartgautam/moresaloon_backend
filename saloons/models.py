from django.db import models
from core.utils.fields import LatitudeField, LongitudeField
import uuid
from country.models import Country,Currency

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
    website_link = models.CharField(max_length=255, null=True)
    facebook_link = models.CharField(max_length=255, null=True)
    instagram_link = models.CharField(max_length=255, null=True)


class Gallery(models.Model):
    id = models.UUIDField( 
        primary_key = True, 
        default = uuid.uuid4, 
        editable = False)
    restaurant = models.ForeignKey(Saloon, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="gallery")