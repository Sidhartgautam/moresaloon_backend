from django.contrib import admin
from services.models import ServiceCategory, Service, ServiceImage

# Register your models here.
admin.site.register(ServiceCategory)
admin.site.register(Service)
admin.site.register(ServiceImage)
