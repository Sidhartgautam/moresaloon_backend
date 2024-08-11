from django.db import models


class LatitudeField(models.FloatField):
    def __init__(
        self,
        verbose_name="Latitude",
        name=None,
        min_value=-90.0,
        max_value=90.0,
        **kwargs
    ):
        self.min_value, self.max_value = min_value, max_value
        models.FloatField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"min_value": self.min_value, "max_value": self.max_value} | kwargs
        return super(LatitudeField, self).formfield(**defaults)


class LongitudeField(models.FloatField):
    def __init__(
        self,
        verbose_name="Longitude",
        name=None,
        min_value=-180.0,
        max_value=180.0,
        **kwargs
    ):
        self.min_value, self.max_value = min_value, max_value
        models.FloatField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"min_value": self.min_value, "max_value": self.max_value} | kwargs
        return super(LongitudeField, self).formfield(**defaults)