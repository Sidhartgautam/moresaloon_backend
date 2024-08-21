from django.urls import path
from .views import( 
StaffListCreateView,
StaffAvailabilityView,
StaffDetailView,
StaffForServiceAPIView,
StaffListByServiceAndSaloonAPIView
)

urlpatterns = [
    path('staff_list_create/<uuid:saloon_id>/', StaffListCreateView.as_view(), name='staff_list_create'),
    path('staff/availability/<uuid:saloon_id>/', StaffAvailabilityView.as_view(), name='staff-availability'),
    path('staff_detail/<int:staff_id>/', StaffDetailView.as_view(), name='staff_detail'),
    path('staff_for_service/<int:service_id>/', StaffForServiceAPIView.as_view(), name='staff_for_service'),
    path('staff_list_by_service_and_saloon/<int:service_id>/<int:saloon_id>/', StaffListByServiceAndSaloonAPIView.as_view(), name='staff_list_by_service_and_saloon'),
]
