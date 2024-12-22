from django.urls import path
from .views import (
    SaloonOfferCreateView,
    SaloonOfferListView,
    CouponCreateView,
    CouponListView,
)

urlpatterns = [
    path('saloon-offers/create/', SaloonOfferCreateView.as_view(), name='saloon-offer-create'),
    path('saloon-offers/', SaloonOfferListView.as_view(), name='saloon-offer-list'),
    path('coupons/create/', CouponCreateView.as_view(), name='coupon-create'),
    path('coupons/', CouponListView.as_view(), name='coupon-list'),
]
