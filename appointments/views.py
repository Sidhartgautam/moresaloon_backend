import requests
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.shortcuts import get_object_or_404
from core.utils.response import PrepareResponse
from core.utils.moredealstoken import get_moredeals_token
from django.db import transaction
import stripe
from staffs.models import BreakTime
from datetime import datetime
from services.models import Service, ServiceVariation
from staffs.models import Staff
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from .models import Appointment, AppointmentSlot
from .serializers import AppointmentSerializer, AppointmentSlotSerializer, AvailableSlotSerializer
from saloons.models import Saloon
from core.utils.pagination import CustomPageNumberPagination
from core.utils.send_mail import send_appointment_confirmation_email
from core.utils.appointment import calculate_total_appointment_price, book_appointment,calculate_appointment_end_time
from datetime import datetime,timedelta

stripe.api_key = settings.STRIPE_SECRET_KEY

# class BookAppointmentAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         print(request.data)
        
#         # Check if the user is authenticated
#         if not request.user.is_authenticated:
#             return PrepareResponse(
#                 success=False,
#                 message="Authentication required.",
#                 errors={"non_field_errors": ["User must be authenticated to book an appointment."]}
#             ).send(403)  # Or another status code if unauthenticated users are allowed to book

#         serializer = AppointmentSerializer(data=data, context={'request': request})

#         if not serializer.is_valid():
#             return PrepareResponse(
#                 success=False,
#                 data=serializer.errors,
#                 message="Appointment booking failed"
#             ).send(400)

#         saloon_id = serializer.validated_data['saloon']
#         print("saloon_id", saloon_id)
#         service_variations = serializer.validated_data['service_variation']
#         print("service_variations", service_variations)
#         staff_id = serializer.validated_data['staff']
#         print("staff_id", staff_id)
#         service_id = serializer.validated_data['service']
#         print("service_id", service_id)
#         slot_id = serializer.validated_data['appointment_slot']
#         print("slot_id", slot_id)

#         if not service_variations:
#             return PrepareResponse(
#                 success=False,
#                 message="Service variations are required."
#             ).send(400)

#         service_variation_id = service_variations[0]
#         print("service_variation_id", service_variation_id)

#         try:
#             slot = AppointmentSlot.objects.get(id=slot_id, staff_id=staff_id, is_available=True)
#         except AppointmentSlot.DoesNotExist:
#             return PrepareResponse(
#                 success=False,
#                 message="Appointment booking failed",
#                 errors={"non_field_errors": ["Slot not available"]}
#             ).send(400)

#         total_amount = calculate_total_appointment_price(service_variations)
#         payment_method = serializer.validated_data.get('payment_method')

#         status, appointment_or_error = self.process_payment(
#             request, payment_method, total_amount, saloon_id, staff_id, service_id, slot_id, service_variation_id
#         )
#         print("status", status)

#         if not status:
#             return PrepareResponse(
#                 success=False,
#                 message="Appointment booking failed",
#                 errors={"non_field_errors": [appointment_or_error]}
#             ).send(400)

#         send_appointment_confirmation_email.delay(appointment_or_error, serializer, saloon_id, request)

#         return PrepareResponse(
#             success=True,
#             message="Appointment booked successfully",
#             data=serializer.data
#         ).send(200)

#     def process_payment(self, request, payment_method, total_amount, saloon_id, staff_id, service_id, slot_id, service_variation_id):
#         if payment_method == 'coa':
#             # Pass the user to book_appointment
#             return book_appointment(request.user, saloon_id, staff_id, service_id, slot_id, service_variation_id)
#         return False
class BookAppointmentAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        if not request.user.is_authenticated:
            return PrepareResponse(
                success=False,
                message="Authentication required.",
                errors={"non_field_errors": ["User must be authenticated to book an appointment."]}
            ).send(403)

        serializer = AppointmentSerializer(data=data, context={'request': request})

        if not serializer.is_valid():
            return PrepareResponse(
                success=False,
                data=serializer.errors,
                message="Appointment booking failed"
            ).send(400)

        validated_data = serializer.validated_data

        saloon_id = validated_data['saloon']
        service_variations_ids = validated_data['service_variation']
        staff_id = validated_data['staff']
        service_id = validated_data['service']
        slot_id = validated_data['appointment_slot']
        buffer_time = validated_data.get('buffer_time', timedelta(minutes=10))
        # Fetch instances
        try:
            saloon = Saloon.objects.get(id=saloon_id)
            service = Service.objects.get(id=service_id, saloon=saloon)
            staff = Staff.objects.get(id=staff_id, saloon=saloon)
            slot = AppointmentSlot.objects.get(id=slot_id, staff=staff, is_available=True)
        except (Saloon.DoesNotExist, Service.DoesNotExist, Staff.DoesNotExist, AppointmentSlot.DoesNotExist):
            return PrepareResponse(
                success=False,
                message="Invalid saloon, service, staff, or slot.",
                errors={"non_field_errors": ["Invalid data provided."]}
            ).send(400)
        # Fetch ServiceVariations based on UUIDs
        print("service_variations_ids 1", service_variations_ids)


        # Calculate end time
        try:
            end_time = calculate_appointment_end_time(
                date=validated_data['date'],
                start_time=validated_data['start_time'],
                service_variations_ids=service_variations_ids,
                buffer_time=buffer_time
            )
        except ValueError as e:
            return PrepareResponse(
                success=False,
                message=str(e)
            ).send(400)

        # Create the appointment
        appointment = Appointment(
            user=request.user,
            saloon=saloon,
            service=service,
            staff=staff,
            appointment_slot=slot,
            date=validated_data['date'],
            start_time=validated_data['start_time'],
            end_time=end_time,
            payment_method=validated_data.get('payment_method')
        )
        appointment.save()

        # Process payment
        total_amount = calculate_total_appointment_price(service_variations_ids)
        payment_method = validated_data.get('payment_method')
        status, appointment_or_error = self.process_payment(
            request, payment_method, total_amount, saloon.id, staff.id, service.id, slot.id, service_variations_ids
        )
        # if not status:
        #     return PrepareResponse(
        #         success=False,
        #         message="Appointment booking failed",
        #         errors={"non_field_errors": [appointment_or_error]}
        #     ).send(400)

        # Send confirmation email
        # send_appointment_confirmation_email.delay(appointment_or_error, serializer, saloon.id, request)
        if status:
            return PrepareResponse(
                success=True,
                message="Appointment booked successfully",
                data=serializer.data
            ).send(200)
        else:
            return PrepareResponse(
                success=False,
                message="Appointment booking failed",
                errors={"non_field_errors": [appointment_or_error]}
            ).send(400)

    def process_payment(self, request, payment_method, total_amount, saloon_id, staff_id, service_id, slot_id, service_variation_ids):
        if payment_method == 'coa':
            return book_appointment(request.user, saloon_id, staff_id, service_id, slot_id, service_variation_ids), "Payment processed successfully"
    
        return False, "Payment method not supported."

class UserAppointmentsListAPIView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Appointments fetched successfully"
        )
        return response.send(200)

class AppointmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    lookup_field = 'appointment_id'
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        appointment_id = self.kwargs.get(self.lookup_field)
        try:
            appointment = Appointment.objects.get(appointment_id=appointment_id)
        except Appointment.DoesNotExist:
            return PrepareResponse(
                success=False,
                message="Appointment not found"
            ).send(404)

        serializer = self.get_serializer(appointment)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Appointment Details"
        )
        return response.send(200)

    def put(self, request, *args, **kwargs):
        appointment_id = self.kwargs.get(self.lookup_field)
        try:
            appointment = Appointment.objects.get(appointment_id=appointment_id)
        except Appointment.DoesNotExist:
            return PrepareResponse(
                success=False,
                message="Appointment not found"
            ).send(404)

        serializer = self.get_serializer(appointment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Appointment updated successfully"
        )
        return response.send(200)

    def delete(self, request, *args, **kwargs):
        appointment_id = self.kwargs.get(self.lookup_field)
        try:
            appointment = Appointment.objects.get(appointment_id=appointment_id)
        except Appointment.DoesNotExist:
            return PrepareResponse(
                success=False,
                message="Appointment not found"
            ).send(404)

        appointment.delete()

        response = PrepareResponse(
            success=True,
            message="Appointment deleted successfully"
        )
        return response.send(204)
    
class AppointmentSlotListAPIView(generics.GenericAPIView):
    serializer_class = AppointmentSlotSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = AppointmentSlot.objects.filter(is_available=True)
        saloon_id = self.kwargs.get('saloon_id')  
        staff_id =self.request.query_params.get('staff_id')
        date =self.request.query_params.get('date')
        service_ids = self.request.query_params.get('service_ids')

        queryset = AppointmentSlot.objects.filter(is_available=True)

        if saloon_id:
            queryset = queryset.filter(saloon_id=saloon_id)
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        if date:
            queryset = queryset.filter(date=date)
        if service_ids:
            staff_with_services = Staff.objects.filter(services__id__in=service_ids).distinct()
            queryset = queryset.filter(staff__in=staff_with_services)
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
            message="Appointment slots fetched successfully",
            data=result,
            meta=paginated_data
        )
        return response.send(code=200)

class AppointmentSlotCreateAPIView(generics.GenericAPIView):
    queryset = AppointmentSlot.objects.all()
    serializer_class = AppointmentSlotSerializer
    # permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        response = PrepareResponse(
            success=True,
            message="Appointment slot created successfully",
            data=serializer.data
        )
        return response.send(201)

    def perform_create(self, serializer):
        serializer.save()

class AppointmentSlotDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AppointmentSlot.objects.all()
    serializer_class = AppointmentSlotSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        appointment_slot = self.get_object()
        serializer = self.get_serializer(appointment_slot)
        response = PrepareResponse(
            success=True,
            message="Appointment slot details fetched successfully",
            data=serializer.data
        )
        return response.send(200)

    def put(self, request, *args, **kwargs):
        appointment_slot = self.get_object()
        serializer = self.get_serializer(appointment_slot, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = PrepareResponse(
            success=True,
            message="Appointment slot updated successfully",
            data=serializer.data
        )
        return response.send(200)

    def delete(self, request, *args, **kwargs):
        appointment_slot = self.get_object()
        appointment_slot.delete()
        response = PrepareResponse(
            success=True,
            message="Appointment slot deleted successfully"
        )
        return response.send(204)
    

class StaffAppointmentsListAPIView(generics.GenericAPIView):
    serializer_class = AppointmentSlotSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        staff_id = self.kwargs.get('staff_id')  # Get staff_id from URL
        queryset = AppointmentSlot.objects.filter(staff_id=staff_id, is_available=True).order_by('start_time')
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
            message="Appointment slots for the staff fetched successfully",
            data=result,
            meta=paginated_data
        )
        return response.send(200)

class CreatedAvailableSlotListAPIView(generics.GenericAPIView):
    serializer_class = AvailableSlotSerializer

    def get_queryset(self):
        staff_id = self.kwargs.get('staff_id')
        date = self.request.query_params.get('date')
        queryset = AppointmentSlot.objects.filter(
            staff_id=staff_id, 
            is_available=True,     
        ).order_by('start_time')

        if date:
            queryset = queryset.filter(date=date)

        return queryset

    def get(self, request, *args, **kwargs):
        date = self.request.query_params.get('date')
        now_date = datetime.now().date()  # Current date without time
        if date:
            try:
                query_date = datetime.strptime(date, "%Y-%m-%d").date()  # Convert date from string to date object
            except ValueError:
                response = PrepareResponse(
                    success=False,
                    message="Invalid date format provided.",
                    data=None
                )
                return response.send(400)

            if query_date < now_date:
                response = PrepareResponse(
                    success=False,
                    message="The requested date is in the past.",
                    data=None
                )
                return response.send(400)
        queryset = self.get_queryset()
        if not queryset.exists():
            response = PrepareResponse(
                success=False,
                message="No available slots found.",
                data=None
            )
            return response.send(404)
        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            message="Available slots created by admin fetched successfully",
            data=serializer.data
        )
        return response.send(200)
    

class AppointmentUpdateAPIView(generics.GenericAPIView):
    serializer_class = AppointmentSlotSerializer
    queryset = AppointmentSlot.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        appointment_slot = self.get_object()
        serializer = self.get_serializer(appointment_slot, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = PrepareResponse(
            success=True,
            message="Appointment slot updated successfully",
            data=serializer.data
        )
        return response.send(200)
    

