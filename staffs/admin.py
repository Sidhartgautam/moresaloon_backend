from django.contrib import admin
from staffs.models import Staff, WorkingDay, BreakTime

# Register your models here.

admin.site.register(Staff) 
admin.site.register(WorkingDay)
admin.site.register(BreakTime) 
