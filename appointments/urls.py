from django.urls import path
from .views import PlaceAppointmentAPIView, UserAppointmentsListAPIView, AppointmentDetailAPIView

urlpatterns = [
    path('place/', PlaceAppointmentAPIView.as_view(), name='place_appointment'),
    path('user/', UserAppointmentsListAPIView.as_view(), name='user_appointments'),
    path('<int:appointment_id>/', AppointmentDetailAPIView.as_view(), name='appointment_detail'),
]
