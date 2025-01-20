import requests
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.shortcuts import get_object_or_404
from core.utils.response import PrepareResponse
from django.utils.dateparse import parse_date
from users.models import User
from django.utils import timezone
from offers.models import CouponUsage
from core.utils.moredealstoken import get_moredeals_token
from django.db import transaction
import stripe
from staffs.models import BreakTime
from datetime import datetime
from services.models import Service, ServiceVariation
from staffs.models import Staff, WorkingDay
from core.utils.fetch_slot import fetch_available_slots
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from .models import Appointment, AppointmentSlot
from .serializers import AppointmentPlaceSerializer, AppointmentSlotSerializer, AvailableSlotSerializer,AppointmentListSerializer,UserAppointmentListSerializer
from saloons.models import Saloon
from core.utils.pagination import CustomPageNumberPagination
from core.utils.mail import send_confirmation_email,staff_confirmation_email,salon_confirmation_email
from core.utils.appointment import calculate_total_appointment_price, book_appointment,calculate_appointment_end_time
from datetime import datetime,timedelta
import random

stripe.api_key = settings.STRIPE_SECRET_KEY


class BookAppointmentAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = AppointmentPlaceSerializer(data=data, context={'request': request})

        if not serializer.is_valid():
            return PrepareResponse(
                success=False,
                data=serializer.errors,
                message="Appointment booking failed"
            ).send(400)

        validated_data = serializer.validated_data
        print("validated data", validated_data)

        start_time = validated_data['start_time']
        saloon_id = validated_data['saloon_id']
        service_variations_ids = validated_data['service_variation_ids']
        staff_id = validated_data['staff_id']
        service_id = validated_data['service_id']
        date = validated_data['date']

        try:
            saloon = Saloon.objects.get(id=saloon_id)
            service = Service.objects.get(id=service_id, saloon=saloon)
            staff = Staff.objects.get(id=staff_id, saloon=saloon)
        except (Saloon.DoesNotExist, Service.DoesNotExist, Staff.DoesNotExist):
            return PrepareResponse(
                success=False,
                message="Invalid saloon, service, or staff.",
                errors={"non_field_errors": ["Invalid data provided."]}
            ).send(400)

        buffer_time = staff.buffer_time

        # Calculate the start time and end time
        try:
            end_time = calculate_appointment_end_time(
                date=validated_data['date'],
                start_time=start_time,
                service_variations_ids=service_variations_ids,
                buffer_time=buffer_time
            )
        except ValueError as e:
            return PrepareResponse(
                success=False,
                message=str(e)
            ).send(400)

        total_price = calculate_total_appointment_price(service_variations_ids)
        coupon = validated_data.get('coupon')
        discount_amount = 0

        if coupon:
            if CouponUsage.objects.filter(coupon=coupon, user=request.user).exists():
                return PrepareResponse(
                    success=False,
                    message="You have already used this coupon."
                ).send(400)

            if coupon.percentage_discount:
                discount_amount = (total_price * coupon.percentage_discount) / 100
            elif coupon.fixed_discount:
                discount_amount = min(coupon.fixed_discount, total_price)

            total_price -= discount_amount

        try:
            with transaction.atomic():
                # Create the appointment
                minimum = pow(10, 10 - 1)
                maximum = pow(10, 10) - 1
                unique_id = random.randint(minimum, maximum)

                appointment = Appointment(
                    user=request.user if request.user.is_authenticated else None,
                    saloon=saloon,
                    service=service,
                    appointment_id=unique_id,
                    staff=staff,
                    date=validated_data['date'],
                    start_time=start_time,
                    end_time=end_time,
                    payment_method=validated_data.get('payment_method'),
                    payment_status='Pending',
                    total_price=total_price,
                    coupon=coupon,
                    fullname=validated_data['fullname'],
                    email=validated_data['email'],
                    phone_number=validated_data['phone_number'],
                    note=validated_data['note'],
                )
                appointment.save()
                appointment.service_variation.add(*service_variations_ids)

                # Apply coupon usage
                if coupon:
                    CouponUsage.objects.create(
                        coupon=coupon,
                        user=request.user,
                        appointment=appointment
                    )

                # Process payment
                payment_status, message, data = self.process_payment(
                    request=request,
                    payment_method=validated_data.get('payment_method'),
                    amount=total_price,
                    user=request.user if request.user.is_authenticated else None,
                    payment_method_id=validated_data.get('payment_method_id'),
                    saloon=saloon,
                    data=data
                )

                if not payment_status:
                    raise ValueError("Payment processing failed.")

                # Update appointment with payment details
                appointment.payment_status = payment_status
                if data:
                    appointment.user_send_amount = data.get('user_send_amount', 0)
                    appointment.transaction_id = data.get('transaction_id', 0)
                    appointment.refferal_points_id = data.get('refferal_points_id', 0)
                appointment.save()

                # Send confirmation emails
                send_confirmation_email(appointment)
                staff_confirmation_email(appointment)
                salon_confirmation_email(appointment)

            return PrepareResponse(
                success=True,
                message="Appointment booked successfully.",
                data=serializer.data
            ).send(200)

        except ValidationError as e:
            return PrepareResponse(
                success=False,
                message="Payment failed",
                errors={"payment_errors": str(e)}
            ).send(400)

        except Exception as e:
            return PrepareResponse(
                success=False,
                message="An error occurred while booking the appointment.",
                errors={"non_field_errors": [str(e)]}
            ).send(500)
    
    def process_payment(self, request, payment_method, amount, user, payment_method_id, saloon, data):
        if payment_method == 'coa':
            return 'Unpaid', "Success", None
        elif payment_method =='stripe':
            try:
                payment_intent = request.data.get('payment_intent')
                if not payment_intent:
                    return "Payment intent not provided", False, None

                payment_intent = stripe.PaymentIntent.confirm(
                    payment_intent,
                      payment_method=payment_method_id,
                      return_url='http://127.0.0.1:8000/appointments/book'
                      )

                if payment_intent['status'] != 'succeeded':
                    raise ValueError(f"Payment failed with status: {payment_intent['status']}")
                    
                else:
                    moredeals_status, message, data = self.stripe_payment(request,amount,saloon, payment_method_id)
                    return moredeals_status, message, data
            except stripe.error.CardError as e:
                raise ValidationError(str(e))
        elif payment_method == 'moredeals':
            try:
                moredeals_status, message, data = self.process_moredeals_payment(request,amount,saloon, payment_method, data)
                return moredeals_status, message, data
            except Exception as e:
                raise ValidationError(str(e))
            
    def get_auth_headers(self, request):
        auth_header=request.headers.get('Authorization')
        return {'Authorization': auth_header} if auth_header else {}

    def stripe_payment(self,request,amount,saloon, payment_method_id):
        try:
            payment_method_get = stripe.PaymentMethod.retrieve(payment_method_id)
            payer_detail = self.get_payer_detail(payment_method_get)
            
            url = "http://192.168.1.72:8000/api/payments/payment-through-stripe/"
            
            response = requests.post(
                url,
                data={
                'amount': amount,
                'payer_detail': payer_detail,
                "brand": payment_method_get['type'],
                'recipient': saloon.user.username,
                'from_project': 'moresaloon',
                'currency_code': saloon.currency.currency_code
                },
                headers=self.get_auth_headers(request)
            )
            if response.status_code == 200:
                payment_data = response.json()['data']

                return 'Paid', "Payment processed successfully", payment_data
            else:
                raise ValidationError("Payment failed: {}".format(response.json().get('error', 'Unknown error')))

        except requests.RequestException as e:
            raise ValidationError(f"Payment request error: {str(e)}")
    
    def get_payer_detail(self, payment_method_get):
        if payment_method_get['type'] == 'card':
            return payment_method_get['card']['last4']
        elif payment_method_get['type'] == 'paypal':
            return payment_method_get['paypal']['payer_email']
        elif payment_method_get['type'] == 'swish':
            return payment_method_get['type']
        return ''
        
    
    def process_moredeals_payment(self, request,amount,saloon, payment_method, data):
        pin = request.data.get('pin')
        if not pin:
            return PrepareResponse(
                success=False,
                message="PIN not provided for MoreDeals payment",
                errors={"non_field_errors": ["PIN not provided for MoreDeals payment"]}
            ).send(400)
        

        url = f"https://moretrek.com/api/payments/payment-through-balance/"
        access_token = get_moredeals_token(request)
        
        response = requests.post(url, data={
            'amount': amount,
            'pin': pin,
            'recipient': saloon.user.username,
            'currency_code': saloon.currency.currency_code,
            'remarks': f'Payment from {payment_method}',
            'platform':'moresaloon'
        }, headers={'Authorization': f"{access_token}"})
        if response.status_code == 200:
            print(response.json())
            return True, "Success", response.json()['data']
        else:
            errors = response.json()['errors']['non_field_errors'][0]
            return False, errors
        
    
class AppointmentListAPIView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        appointments = Appointment.objects.all()
        serializer = AppointmentListSerializer(appointments, many=True)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Appointments fetched successfully"
        )
        return response.send(200)

    
class UserAppointmentsListAPIView(generics.ListAPIView):
    serializer_class = UserAppointmentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id=self.request.user if self.request.user.is_authenticated else None
        queryset = Appointment.objects.filter(user=user_id)
        date_param = self.request.query_params.get('date', None)
        if date_param:
            try:
                date = parse_date(date_param)
                if date:
                    queryset = queryset.filter(date=date)
            except ValueError:
                pass  
        
        return queryset

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
    serializer_class = AppointmentPlaceSerializer
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
# class AvailableSlotListAPIView(generics.GenericAPIView):
#     serializer_class = AvailableSlotSerializer

#     def get_queryset(self):
#         staff_id = self.kwargs.get('staff_id')
#         date = self.request.query_params.get('date')
#         service_variations = self.request.query_params.getlist('service_variation', [])

#         # Check if service_variation is provided
#         if not service_variations:
#             print("No service variations provided.")
#             return []

#         if not date:
#             return []

#         try:
#             date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         except ValueError:
#             return []

#         # Get the staff and check if they are on holiday
#         staff = get_object_or_404(Staff, id=staff_id)
#         if staff.is_holiday:
#             print(f"Staff {staff.name} is on holiday.")
#             return []  # Return empty if staff is on holiday

#         # Get the day name based on the date
#         day_name = date_obj.strftime("%A")

#         # Get booked appointments to avoid overlapping slots
#         booked_appointments = Appointment.objects.filter(staff_id=staff_id, date=date).values_list('start_time', 'end_time')

#         available_slots = []
#         buffer_time = staff.buffer_time or timedelta(minutes=10)  # Default buffer time

#         # Get staff working hours for that day
#         working_day = staff.working_days.filter(day_of_week=day_name).first()
#         if not working_day:
#             print(f"No working day found for {day_name}")
#             return []

#         # Check if working day has valid start and end times
#         if not working_day.start_time or not working_day.end_time:
#             print(f"Working day {day_name} found, but missing start or end time.")
#             return []

#         current_time = working_day.start_time
#         end_time = working_day.end_time

#         # Calculate total duration from service variations
#         total_duration = timedelta()
#         for sv in service_variations:
#             svd = ServiceVariation.objects.get(id=sv)
#             total_duration += svd.duration

#         while current_time < end_time:
#             slot_end_time = (datetime.combine(datetime.today(), current_time) + total_duration + buffer_time).time()

#             if slot_end_time > end_time:
#                 break

#             # Check if the slot overlaps with any booked appointment
#             overlapping_appointments = [
#                 (start_time, end_time)
#                 for start_time, end_time in booked_appointments
#                 if not (slot_end_time <= start_time or current_time >= end_time)
#             ]

#             if not overlapping_appointments:
#                 available_slots.append({
#                     'start_time': current_time,
#                     'end_time': slot_end_time,
#                     'service_variations': service_variations,
#                 })
#             current_time = (datetime.combine(datetime.today(), current_time) + total_duration + buffer_time).time()
            

#         return available_slots

#     def get(self, request, *args, **kwargs):
#         date = self.request.query_params.get('date')
#         now_date = datetime.now().date()
#         if date:
#             try:
#                 query_date = datetime.strptime(date, "%Y-%m-%d").date()
#                 if query_date < now_date:
#                     return PrepareResponse(
#                         success=False,
#                         message="The requested date is in the past.",
#                         data=None
#                     ).send(400)
#             except ValueError:
#                 return PrepareResponse(
#                     success=False,
#                     message="Invalid date format provided. Use 'YYYY-MM-DD'.",
#                     data=None
#                 ).send(400)

#         queryset = self.get_queryset()
#         if not queryset:
#             return PrepareResponse(
#                 success=False,
#                 message="No available slots found.",
#                 data=None
#             ).send(404)

#         serializer = self.get_serializer(queryset, many=True)
#         return PrepareResponse(
#             success=True,
#             message="Available slots fetched successfully.",
#             data=serializer.data
#         ).send(200)

class AvailableSlotListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        staff_id = self.kwargs.get("staff_id")
        saloon_id = self.request.query_params.get("saloon_id")
        date_str = request.query_params.get("date")
        service_variations = request.query_params.getlist("service_variation", [])

        # Debugging logs
        print(f"DEBUG: Staff ID: {staff_id}")
        print(f"DEBUG: Saloon ID: {saloon_id}")
        print(f"DEBUG: Date: {date_str}")
        print(f"DEBUG: Service Variations: {service_variations}")

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            print(f"DEBUG: Parsed Date: {date}")
        except (ValueError, TypeError):
            print(f"DEBUG: Invalid date format: {date_str}")
            return PrepareResponse(
                success=False,
                message="Invalid date format provided. Use 'YYYY-MM-DD'.",
                data=None,
            ).send(400)

        if not service_variations:
            print("DEBUG: No service variations provided.")
            return PrepareResponse(
                success=False,
                message="No service variations provided.",
                data=None,
            ).send(400)

        # Get saloon and staff details
        try:
            saloon = Saloon.objects.get(id=saloon_id)
            print(f"DEBUG: Saloon Timezone: {saloon.timezone}")

            staff = Staff.objects.get(id=staff_id)
            print(f"DEBUG: Staff Name: {staff.name}, Is Holiday: {staff.is_holiday}")

            if staff.is_holiday:
                print(f"DEBUG: Staff {staff.name} is on holiday.")
                return PrepareResponse(
                    success=False,
                    message=f"Staff {staff.name} is on holiday.",
                    data=None,
                ).send(400)

            # Fetch slots
            slots = fetch_available_slots(saloon, staff, date, service_variations)
            if not slots:
                print("DEBUG: No available slots found.")
                return PrepareResponse(
                    success=False,
                    message="No available slots found.",
                    data=None,
                ).send(404)

            print(f"DEBUG: Available Slots: {slots}")
            return PrepareResponse(
                success=True,
                message="Available slots fetched successfully.",
                data=slots,
            ).send(200)

        except Saloon.DoesNotExist:
            print(f"DEBUG: Saloon with ID {saloon_id} not found.")
            return PrepareResponse(
                success=False,
                message="Saloon not found.",
                data=None,
            ).send(404)

        except Staff.DoesNotExist:
            print(f"DEBUG: Staff with ID {staff_id} not found.")
            return PrepareResponse(
                success=False,
                message="Staff not found.",
                data=None,
            ).send(404)

        except Exception as e:
            print(f"DEBUG: An unexpected error occurred: {str(e)}")
            return PrepareResponse(
                success=False,
                message="An unexpected error occurred.",
                data={"error": str(e)},
            ).send(500)



        
    

