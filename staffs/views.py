from rest_framework import generics, status
from rest_framework.response import Response
from .models import Staff, WorkingDay
from .serializers import StaffSerializer
from core.utils.response import PrepareResponse
from datetime import datetime, timedelta
from appointments.models import Appointment

class StaffListCreateView(generics.ListCreateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

class StaffAvailabilityView(generics.GenericAPIView):
    serializer_class = StaffSerializer

    def post(self, request, *args, **kwargs):
        staff_id = request.data.get('staff_id')
        appointment_date = request.data.get('appointment_date')
        appointment_start_time = request.data.get('start_time')
        appointment_end_time = request.data.get('end_time')

        staff = Staff.objects.get(id=staff_id)
        working_day = WorkingDay.objects.filter(staff=staff, day_of_week=appointment_date.strftime('%A')).first()

        if not working_day:
            response = PrepareResponse(success=False, message='Staff is not available on this day.')
            return response.send(status.HTTP_400_BAD_REQUEST)

        if not (working_day.start_time <= appointment_start_time <= working_day.end_time) or not (working_day.start_time <= appointment_end_time <= working_day.end_time):
            response = PrepareResponse(success=False, message='Appointment time is outside of working hours.')
            return response.send(status.HTTP_400_BAD_REQUEST)

        break_times = working_day.break_times.all()
        for break_time in break_times:
            if (break_time.break_start <= appointment_start_time < break_time.break_end) or (break_time.break_start < appointment_end_time <= break_time.break_end):
                response = PrepareResponse(success=False, message='Appointment overlaps with break time.')
                return response.send(status.HTTP_400_BAD_REQUEST)

        overlapping_appointments = Appointment.objects.filter(staff=staff, date=appointment_date).exclude(end_time__lte=appointment_start_time).exclude(start_time__gte=appointment_end_time)
        if overlapping_appointments.exists():
            response = PrepareResponse(success=False, message='Appointment time overlaps with another booking.')
            return response.send(status.HTTP_400_BAD_REQUEST)

        response = PrepareResponse(success=True, message='Staff is available.')
        return response.send(status.HTTP_200_OK)
