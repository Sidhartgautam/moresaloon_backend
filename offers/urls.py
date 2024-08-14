from django.urls import path
from .views import SaloonOfferListView, SaloonSpecificOfferListView, SaloonOfferCreateView

urlpatterns = [
    path('list/', SaloonOfferListView.as_view(), name='saloon_offer_list'),
    path('<uuid:saloon_id>/', SaloonSpecificOfferListView.as_view(), name='saloon_specific_offer'),
    path('create/', SaloonOfferCreateView.as_view(), name='saloon_offer_create'),
]
