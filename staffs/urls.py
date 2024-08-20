from django.urls import path
from .views import( StaffListView,
StaffCreateView,
StaffAvailabilityView,
StaffListOnlyView,
StaffForServiceAPIView
)

urlpatterns = [
    path('staff_list/<uuid:saloon_id>/', StaffListView.as_view(), name='staff_list'),
    path('staff_create/', StaffCreateView.as_view(), name='staff_create'),
    path('staff/availability/<uuid:saloon_id>/', StaffAvailabilityView.as_view(), name='staff-availability'),
    path('staff_list_only/<int:staff_id>/', StaffListOnlyView.as_view(), name='staff_list_only'),
    path('staff_for_service/<int:service_id>/', StaffForServiceAPIView.as_view(), name='staff_for_service'),

]