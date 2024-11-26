from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=50)
    currency_code = models.CharField(max_length=3)
    symbol = models.CharField(max_length=3, null=True)

    def __str__(self):
        return self.name
    
# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=50)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=2)

    class Meta:
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name
    

    
