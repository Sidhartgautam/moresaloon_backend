from django.contrib import admin
from .models import ServiceCategory, Service, ServiceVariation, ServiceImage

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_duration']

@admin.register(ServiceVariation)
class ServiceVariationAdmin(admin.ModelAdmin):
    list_display = ['service', 'name', 'additional_duration', 'total_duration']


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ['service', 'image']