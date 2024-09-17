from django.contrib import admin
from .models import SaloonOffer
from services.models import ServiceVariation

class SaloonOfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'saloon', 'original_price', 'offer_price', 'start_offer', 'end_offer')


admin.site.register(SaloonOffer, SaloonOfferAdmin)