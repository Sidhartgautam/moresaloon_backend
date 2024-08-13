from django.urls import path
from .views import( StaffListView,
StaffCreateView, 
# StaffAvailabilityView
)

urlpatterns = [
    path('staff_list/<uuid:saloon_id>/', StaffListView.as_view(), name='staff_list'),
    path('staff_create/', StaffCreateView.as_view(), name='staff_create'),
    # path('staff_availability/', StaffAvailabilityView.as_view(), name='staff_availability'),
]