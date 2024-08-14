from rest_framework import generics, status
from rest_framework.response import Response
from .models import Staff, WorkingDay
from rest_framework.permissions import IsAuthenticated
from .serializers import StaffSerializer
from core.utils.response import PrepareResponse
from datetime import datetime, timedelta
from appointments.models import Appointment
from core.utils.pagination import CustomPageNumberPagination

class StaffListView(generics.GenericAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        saloon_id = self.kwargs.get('saloon_id')
        queryset = Staff.objects.all()

        if saloon_id:
            queryset = queryset.filter(saloon_id=saloon_id)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(page, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data)
        result = paginated_data['results']
        del paginated_data['results']
        response = PrepareResponse(
            success=True,
            data=result,
            message="Staff list fetched successfully",
            meta=paginated_data
        )
        return response.send(200)
    
class StaffCreateView(generics.GenericAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = PrepareResponse(
                success=True,
                data=serializer.data,
                message="Staff member created successfully"
            )
            return response.send(201)
        
        response = PrepareResponse(
            success=False,
            data=serializer.errors,
            message="Failed to create staff member"
        )
        return response.send(400)
# class StaffAvailabilityView(generics.GenericAPIView):
#     serializer_class = StaffSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             staff_id = request.data.get('staff_id')
#             appointment_date = request.data.get('appointment_date')
#             appointment_start_time = request.data.get('start_time')
#             appointment_end_time = request.data.get('end_time')
#             try:
#                 staff = Staff.objects.get(id=staff_id)
#             except Staff.DoesNotExist:
#                 response = PrepareResponse(success=False, message='Staff not found.')
#                 return response.send(404)

#             try:
#                 appointment_date = appointment_date  # Assuming appointment_date is already a valid date object
#             except ValueError:
#                 response = PrepareResponse(success=False, message='Invalid date format.')
#                 return response.send(400)

#             working_day = WorkingDay.objects.filter(staff=staff, day_of_week=appointment_date.strftime('%A')).first()

#             if not working_day:
#                 response = PrepareResponse(success=False, message='Staff is not available on this day.')
#                 return response.send(400)

#             if not (working_day.start_time <= appointment_start_time <= working_day.end_time) or not (working_day.start_time <= appointment_end_time <= working_day.end_time):
#                 response = PrepareResponse(success=False, message='Appointment time is outside of working hours.')
#                 return response.send(400)

#             break_times = working_day.break_times.all()
#             for break_time in break_times:
#                 if (break_time.break_start <= appointment_start_time < break_time.break_end) or (break_time.break_start < appointment_end_time <= break_time.break_end):
#                     response = PrepareResponse(success=False, message='Appointment overlaps with break time.')
#                     return response.send(400)

#             overlapping_appointments = Appointment.objects.filter(staff=staff, date=appointment_date).exclude(end_time__lte=appointment_start_time).exclude(start_time__gte=appointment_end_time)
#             if overlapping_appointments.exists():
#                 response = PrepareResponse(success=False, message='Appointment time overlaps with another booking.')
#                 return response.send(400)

#             response = PrepareResponse(success=True, message='Staff is available.')
#         else:
#             response = PrepareResponse(success=False, message='Invalid request data.', errors=serializer.errors)
#             return response.send(400)