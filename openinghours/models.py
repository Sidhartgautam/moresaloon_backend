from django.db import models
from saloons.models import Saloon

# Create your models here.
class OpeningHour(models.Model):
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=9, choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')])
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_open = models.BooleanField(default=True)

    class Meta:
        unique_together = ('saloon', 'day_of_week')

    def __str__(self):
        return f"{self.saloon.name} - {self.day_of_week} - {self.start_time} - {self.end_time}"
