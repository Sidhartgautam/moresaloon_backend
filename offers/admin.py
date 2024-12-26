from django.contrib import admin
from .models import SaloonOffers, SaloonCoupons, CouponUsage


admin.site.register(SaloonOffers)
admin.site.register(SaloonCoupons)
admin.site.register(CouponUsage)
