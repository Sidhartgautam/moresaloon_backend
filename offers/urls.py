from django.urls import path
from .views import (
    SaloonOfferCreateView,
    SaloonOfferListView,
    CouponCreateView,
    CouponListView,
    CheckCouponValidityAPIView
)

urlpatterns = [
    path('saloon-offers/create/', SaloonOfferCreateView.as_view(), name='saloon-offer-create'),
    path('saloon-offers/list/', SaloonOfferListView.as_view(), name='saloon-offer-list'),
    path('coupons/create/', CouponCreateView.as_view(), name='coupon-create'),
    path('coupons/lists/<uuid:saloon_id>/', CouponListView.as_view(), name='coupon-list'),
    path('coupons/check/', CheckCouponValidityAPIView.as_view(), name='check-coupon-validity'),
]
