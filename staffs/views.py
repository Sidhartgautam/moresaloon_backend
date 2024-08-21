from rest_framework import generics, status
from .models import Staff, WorkingDay
from rest_framework.permissions import IsAuthenticated
from .serializers import StaffSerializer, StaffAvailabilitySerializer, StaffListSerializer
from core.utils.response import PrepareResponse
from appointments.models import Appointment
from core.utils.pagination import CustomPageNumberPagination

from django.db.models import Q

class StaffListCreateView(generics.GenericAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
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
    
class StaffAvailabilityView(generics.GenericAPIView):
    serializer_class = StaffAvailabilitySerializer

    def post(self, request, *args, **kwargs):
        saloon_id = self.kwargs.get('saloon_id')
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            staff_id = serializer.validated_data.get('staff_id')
            appointment_date = serializer.validated_data.get('appointment_date')
            appointment_start_time = serializer.validated_data.get('start_time')
            appointment_end_time = serializer.validated_data.get('end_time')

            staff = Staff.objects.filter(id=staff_id, saloon_id=saloon_id).first()
            if not staff:
                response = PrepareResponse(success=False, message='Staff not found in the specified saloon.')
                return response.send(404)

            working_day = WorkingDay.objects.filter(
                staff=staff,
                day_of_week=appointment_date.strftime('%A')
            ).first()
            
            if not working_day:
                response = PrepareResponse(success=False, message='Staff is not available on this day.')
                return response.send(400)
            
            print(f"Working Day: {working_day}")
            print(f"Appointment Start Time: {appointment_start_time}")
            print(f"Appointment End Time: {appointment_end_time}")

            if not (working_day.start_time <= appointment_start_time < working_day.end_time and
                    working_day.start_time < appointment_end_time <= working_day.end_time):
                response = PrepareResponse(success=False, message='Appointment time is outside of working hours.')
                return response.send(400)

            break_times = working_day.break_times.all()
            for break_time in break_times:
                if (break_time.break_start < appointment_end_time and break_time.break_end > appointment_start_time):
                    response = PrepareResponse(success=False, message='Appointment overlaps with break time.')
                    return response.send(400)

            overlapping_appointments = Appointment.objects.filter(
                staff=staff,
                date=appointment_date
            ).exclude(end_time__lte=appointment_start_time).exclude(start_time__gte=appointment_end_time)

            if overlapping_appointments.exists():
                response = PrepareResponse(success=False, message='Appointment time overlaps with another booking.')
                return response.send(400)

            response = PrepareResponse(success=True, message='Staff is available.')
        else:
            response = PrepareResponse(success=False, message='Invalid request data.', errors=serializer.errors)
            return response.send(400)
        
        return response.send(200)
    
class StaffDetailView(generics.GenericAPIView):
    serializer_class = StaffListSerializer

    def get_queryset(self):
        staff_id = self.kwargs.get('staff_id')
        queryset = Staff.objects.filter(id=staff_id)
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            response = PrepareResponse(
                success=False,
                message="Staff not found",
                data=None
            )
            return response.send(404)
        staff = queryset.first()
        serializer = self.get_serializer(staff)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Staff details fetched successfully"
        )
        return response.send(200)

class StaffForServiceAPIView(generics.GenericAPIView):
    serializer_class = StaffListSerializer

    def get_queryset(self):
        service_id = self.request.query_params.get('service_id')  # Get the service ID from query parameters
        queryset = Staff.objects.all()
        if service_id:
            queryset = queryset.filter(services__id=service_id)  # Filter staff by the service
        return queryset
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            message="Staff members for the selected service fetched successfully",
            data=serializer.data
        )
        return response.send(200)
    
class StaffListByServiceAndSaloonAPIView(generics.GenericAPIView):
    serializer_class = StaffListSerializer

    def get_queryset(self):
        service_id = self.request.query_params.get('service_id') 
        saloon_id = self.request.query_params.get('saloon_id') 

        queryset = Staff.objects.filter(
            saloon_id=saloon_id, 
            services__id=service_id
        ).select_related('saloon').prefetch_related('services')

        return queryset    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exist():
            return PrepareResponse(
                success=False,
                message="No staff found for the selected service and saloon"               
            ).send (404)
        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            message="Staff members for the selected service and saloon fetched successfully",
            data=serializer.data
        )
        return response.send(200)
        