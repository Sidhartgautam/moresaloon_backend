from django.urls import path
from .views import(
     BookAppointmentAPIView,
       UserAppointmentsListAPIView, 
       AppointmentDetailAPIView, 
       AppointmentSlotListAPIView,
       AppointmentSlotCreateAPIView,
       AppointmentSlotDetailAPIView,
       StaffAppointmentsListAPIView,
       CreatedAvailableSlotListAPIView,
       AppointmentListAPIView
)

urlpatterns = [
    path('place/', BookAppointmentAPIView.as_view(), name='place_appointment'),
    path('list/', AppointmentListAPIView.as_view(), name='appointment_list'),
    path('user/', UserAppointmentsListAPIView.as_view(), name='user_appointments'),
    path('<int:appointment_id>/', AppointmentDetailAPIView.as_view(), name='appointment_detail'),
    path('appointment-slots/<uuid:saloon_id>/', AppointmentSlotListAPIView.as_view(), name='appointment-slot-list'),
    path('slots/create/', AppointmentSlotCreateAPIView.as_view(), name='appointment-slot-create'),
    path('appointment-slots/<uuid:id>/', AppointmentSlotDetailAPIView.as_view(), name='appointment-slot-detail'),
    path('staff-appointments/<int:staff_id>/', StaffAppointmentsListAPIView.as_view(), name='staff-appointments-list'),
    path('available-slots/<uuid:staff_id>/', CreatedAvailableSlotListAPIView.as_view(), name='admin-available-slots'),
]
