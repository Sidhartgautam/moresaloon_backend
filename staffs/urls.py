from django.urls import path
from .views import StaffListCreateView, StaffAvailabilityView

urlpatterns = [
    path('staff_list/', StaffListCreateView.as_view(), name='staff_list'),
    path('staff_availability/', StaffAvailabilityView.as_view(), name='staff_availability'),
]