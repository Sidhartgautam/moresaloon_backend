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
from staffs.models import Staff
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from .models import Appointment, AppointmentSlot
from .serializers import AppointmentSerializer, AppointmentSlotSerializer, AvailableSlotSerializer
from saloons.models import Saloon
from core.utils.pagination import CustomPageNumberPagination
from core.utils.send_mail import send_appointment_confirmation_email
from core.utils.appointment import calculate_total_appointment_price, book_appointment

stripe.api_key = settings.STRIPE_SECRET_KEY

# class PlaceAppointmentAPIView(APIView):
#     # permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         serializer = AppointmentSerializer(data=data, context={'request': request})

#         if serializer.is_valid():
#             # Check for appointment slot and availability conflicts
#             staff = serializer.validated_data.get('staff')
#             start_time = serializer.validated_data.get('start_time')
#             end_time = serializer.validated_data.get('end_time')

#             # Ensure no overlapping appointments for the same staff
#             overlapping_appointments = Appointment.objects.filter(
#                 staff=staff,
#                 start_time__lt=end_time,
#                 end_time__gt=start_time
#             ).exists()

#             if overlapping_appointments:
#                 raise ValidationError("This time slot is already booked for the selected staff.")

#             # Check for staff break time conflicts
#             break_times = BreakTime.objects.filter(
#                 working_day__staff=staff,
#                 start_time__lt=end_time,
#                 end_time__gt=start_time
#             )
#             if break_times.exists():
#                 raise ValidationError("This time slot conflicts with the staff's break time.")

#             # Ensure no duplicate appointments for the same user in the same time slot
#             user = request.user
#             duplicate_appointments = Appointment.objects.filter(
#                 user=user,
#                 start_time__lt=end_time,
#                 end_time__gt=start_time
#             ).exists()

#             if duplicate_appointments:
#                 raise ValidationError("You already have an appointment during this time slot.")

#             # Handle payment and save the appointment
#             saloon_id = serializer.validated_data.get('saloon').id
#             saloon = get_object_or_404(Saloon, id=saloon_id)
#             payment_method = serializer.validated_data.get('payment_method')
#             appointment = serializer.save(user=user)
#             total_price = appointment.total_price

#             if payment_method == 'coa':
#                 pass
#             elif payment_method == 'stripe':
#                 try:
#                     if request.data.get('payment_intent') is not None:
#                         payment_confirm = stripe.PaymentIntent.retrieve(request.data.get('payment_intent'))
#                         if payment_confirm['status'] != 'succeeded':
#                             raise ValidationError("Payment failed with status: " + payment_confirm['status'])
#                     else:
#                         raise ValidationError("Payment intent not provided")
#                 except stripe.error.StripeError as e:
#                     raise ValidationError(f"Stripe error: {e.user_message}")
#             elif payment_method == 'moredeals':
#                 if request.data.get('pin') is not None:
#                     url = f"https://moretrek.com/api/payments/payment-through-balance/"
#                     access_token = get_moredeals_token(request)
#                     response = requests.post(url, data={
#                         'amount': total_price,
#                         'pin': request.data.get('pin'),
#                         'recipient': saloon.user.username,
#                         'currency_code': saloon.currency.currency_code
#                     }, headers={'Authorization': f"{access_token}"})
#                     if response.status_code != 200:
#                         errors = response.json().get('errors', {}).get('non_field_errors', ['Payment failed'])
#                         return PrepareResponse(success=False, message=errors[0]).send(400)
#                 else:
#                     return PrepareResponse(success=False, message="PIN not provided for MoreDeals payment").send(400)

#             if appointment:
#                 send_appointment_confirmation_email.delay(
#                     'Appointment Confirmation',
#                     'Your appointment is confirmed.',
#                     [saloon.email]  # Send to the saloon's email
#                 )
#                 return PrepareResponse(success=True, message="Appointment placed successfully", data=serializer.data).send(200)
#             else:
#                 raise ValidationError("Appointment processing failed")
#         else:
#             return PrepareResponse(success=False, data=serializer.errors, message="Appointment failed").send(400)


class BookAppointmentAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = AppointmentSerializer(data=data, context={'request': request})

        # Validate incoming data
        if not serializer.is_valid():
            return PrepareResponse(
                success=False,
                data=serializer.errors,
                message="Appointment booking failed"
            ).send(400)

        # Retrieve saloon information
        saloon_id = serializer.validated_data['saloon_id']
        saloon = get_object_or_404(Saloon, id=saloon_id, country__code=request.country_code)
        
        # Retrieve service(s) being booked
        services = serializer.validated_data.get('services')
        if not services:
            return PrepareResponse(
                success=False,
                message="Appointment booking failed",
                errors={"non_field_errors": ["Please select at least one service"]}
            ).send(400)

        # Calculate the total appointment price
        total_amount = calculate_total_appointment_price(request, services, saloon_id)
        if total_amount is None:
            return PrepareResponse(
                success=False,
                message="Appointment calculation failed",
                errors={"non_field_errors": ["There was an issue with the service selection."]}
            ).send(400)

        # Handle payment and booking logic
        payment_method = serializer.validated_data.get('payment_method')
        payment_method_id = serializer.validated_data.get('payment_method_id')

        # Process the booking
        status, appointment = self.process_payment(request, payment_method, payment_method_id, total_amount, saloon, data)
        
        if not status:
            return PrepareResponse(
                success=False,
                message="Appointment booking failed",
                errors={"non_field_errors": [appointment]}
            ).send(400)

        # Send appointment confirmation emails
        send_appointment_confirmation_email.delay(appointment, serializer, saloon, request)

        return PrepareResponse(
            success=True,
            message="Appointment booked successfully",
            data=serializer.data
        ).send(200)

    def process_payment(self, request, payment_method, payment_method_id, total_amount, saloon, data):
        # If payment is cash on delivery (or pay at salon)
        if payment_method == 'cod':
            return book_appointment(request, data)
        return False, "Invalid payment method"


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
    

