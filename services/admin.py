from django.contrib import admin
from .models import  Service, ServiceVariation, ServiceImage,ServiceVariationImage


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_duration','min_duration']

@admin.register(ServiceVariation)
class ServiceVariationAdmin(admin.ModelAdmin):
    list_display = ['service', 'name', 'duration', 'price','description','discount_price']
    


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ['service', 'image']

@admin.register(ServiceVariationImage)
class ServiceVariationImageAdmin(admin.ModelAdmin):
    list_display = ['variation', 'image']