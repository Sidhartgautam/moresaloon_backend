from django.contrib import admin
from .models import Appointment, AppointmentSlot
from datetime import datetime

class AppointmentAdmin(admin.ModelAdmin):

    fields = (
        'user', 'saloon', 'service', 'service_variation', 
        'staff','date',  'start_time', 'status', 
        'payment_status', 'payment_method', 'total_price','fullname', 'email', 'phone_number', 'note','currency'
    )
    readonly_fields = ('end_time',)  # Make end_time readonly if you want to display it but not edit

    def save_model(self, request, obj, form, change):
        # Calculate end_time based on service_variation duration if available
        if obj.start_time and obj.service_variation.exists():
            service_duration = obj.service_variation.first().duration
            start_datetime = datetime.combine(obj.date, obj.start_time)
            end_datetime = start_datetime + service_duration
            obj.end_time = end_datetime.time()
        else:
            obj.end_time = None

        super().save_model(request, obj, form, change)

admin.site.register(Appointment, AppointmentAdmin)

@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'saloon', 'staff', 'service', 'start_time', 'end_time','working_day']
    list_filter = ['saloon', 'staff', 'service']
    search_fields = ['saloon__name', 'staff__name', 'service__name']

    # sum(v.duration for v in obj.service_variation.all())


