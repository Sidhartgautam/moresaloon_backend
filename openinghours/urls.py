from django.urls import path
from .views import OpeningHoursCreateView, OpeningHoursListView

urlpatterns = [
    path('create/', OpeningHoursCreateView.as_view(), name='opening_hours_create'),
    path('list/', OpeningHoursListView.as_view(), name='opening_hours_list'),
]