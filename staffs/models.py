from django.db import models
from saloons.models import Saloon
# from django.contrib.auth.models import User

class Staff(models.Model):
    # user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    saloon = models.ForeignKey(Saloon, related_name='staffs', on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.saloon.name if self.saloon else 'No Saloon'}"

class WorkingDay(models.Model):
    staff = models.ForeignKey(Staff, related_name='working_days', on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=9, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.staff.name} - {self.day_of_week}-{self.start_time} to {self.end_time}"

class BreakTime(models.Model):
    working_day = models.ForeignKey(WorkingDay, related_name='break_times', on_delete=models.CASCADE)
    break_start = models.TimeField()
    break_end = models.TimeField()

    def __str__(self):
        return f" {self.working_day.staff.name} - {self.break_start} to {self.break_end}"
