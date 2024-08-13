from django.urls import path
from .views import(
     PlaceAppointmentAPIView,
       UserAppointmentsListAPIView, 
       AppointmentDetailAPIView, 
       AppointmentSlotListAPIView,
       AppointmentSlotCreateAPIView,
       AppointmentSlotDetailAPIView
)

urlpatterns = [
    path('place/', PlaceAppointmentAPIView.as_view(), name='place_appointment'),
    path('user/', UserAppointmentsListAPIView.as_view(), name='user_appointments'),
    path('<int:appointment_id>/', AppointmentDetailAPIView.as_view(), name='appointment_detail'),
    path('slots/', AppointmentSlotListAPIView.as_view(), name='appointment-slot-list'),
    path('slots/create/', AppointmentSlotCreateAPIView.as_view(), name='appointment-slot-create'),
    path('appointment-slots/<uuid:id>/', AppointmentSlotDetailAPIView.as_view(), name='appointment-slot-detail'),
]
