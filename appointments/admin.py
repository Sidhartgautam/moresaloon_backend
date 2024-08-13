from django.contrib import admin
from .models import Appointment, AppointmentSlot
from datetime import datetime

class AppointmentAdmin(admin.ModelAdmin):
    exclude = ('end_time',)  # Exclude end_time from admin form

    fields = ('user', 'saloon', 'service', 'staff', 'date', 'start_time', 'status', 'payment_status', 'payment_method')
    readonly_fields = ('end_time',)  # Make end_time readonly if you want to display it but not edit

    def save_model(self, request, obj, form, change):
        if obj.start_time and obj.service and obj.service.duration:
            obj.end_time = (datetime.combine(datetime.today(), obj.start_time) + obj.service.duration).time()
        super().save_model(request, obj, form, change)

admin.site.register(Appointment, AppointmentAdmin)

@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ['saloon', 'staff', 'service', 'date', 'start_time', 'end_time', 'is_available']
    list_filter = ['saloon', 'staff', 'service', 'date']
    search_fields = ['saloon__name', 'staff__name', 'service__name', 'date']