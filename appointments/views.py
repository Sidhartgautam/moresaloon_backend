import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.shortcuts import get_object_or_404
from core.utils.response import PrepareResponse
from core.utils.moredealstoken import get_moredeals_token
from rest_framework.generics import GenericAPIView
import stripe
from django.conf import settings
from django.core.mail import send_mail
from .models import Appointment, AppointmentSlot
from .serializers import AppointmentSerializer, AppointmentSlotSerializer
from saloons.models import Saloon
from core.utils.pagination import CustomPagination

stripe.api_key = settings.STRIPE_SECRET_KEY

class PlaceAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = AppointmentSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            saloon_id = serializer.validated_data.get('saloon').id
            saloon = get_object_or_404(Saloon, id=saloon_id)
            payment_method = serializer.validated_data.get('payment_method')
            appointment = None

            if payment_method == 'coa':
                appointment = serializer.save(user=request.user)
            elif payment_method == 'stripe':
                try:
                    if request.data.get('payment_intent') is not None:
                        payment_confirm = stripe.PaymentIntent.retrieve(request.data.get('payment_intent'))
                        if payment_confirm['status'] == 'succeeded':
                            appointment = serializer.save(user=request.user)
                        else:
                            raise ValueError("Payment failed with status: " + payment_confirm['status'])
                    else:
                        raise ValueError("Payment intent not provided")
                except stripe.error.StripeError as e:
                    raise ValueError(f"Stripe error: {e.user_message}")
            elif payment_method == 'moredeals':
                if request.data.get('pin') is not None:
                    url = f"https://moretrek.com/api/payments/payment-through-balance/"
                    access_token = get_moredeals_token(request)
                    response = requests.post(url, data={
                        'amount': serializer.validated_data['service'].price,
                        'pin': request.data.get('pin'),
                        'recipient': saloon.user.username,
                        'currency_code': saloon.currency.currency_code
                    }, headers={'Authorization': f"{access_token}"})
                    if response.status_code == 200:
                        appointment = serializer.save(user=request.user)
                    else:
                        errors = response.json()['errors']['non_field_errors'][0]
                        response_json = PrepareResponse(
                            success=False,
                            message=errors,
                            errors={"non_field_errors": [errors]}
                        )
                        return response_json.send(status.HTTP_400_BAD_REQUEST)
                else:
                    response_json = PrepareResponse(
                        success=False,
                        message="PIN not provided for MoreDeals payment",
                        errors={"non_field_errors": ["PIN not provided for MoreDeals payment"]}
                    )
                    return response_json.send(status.HTTP_400_BAD_REQUEST)

            if appointment:
                send_mail(
                    'Appointment Confirmation',
                    'Your appointment is confirmed.',
                    'sender@example.com',
                    [saloon.email],
                )
                response = PrepareResponse(
                    success=True,
                    message="Appointment placed successfully",
                    data=serializer.data
                )
                return response.send(status.HTTP_200_OK)
            else:
                raise ValueError("Appointment processing failed")
        else:
            response = PrepareResponse(
                success=False,
                data=serializer.errors,
                message="Appointment failed"
            )
            return response.send(status.HTTP_400_BAD_REQUEST)

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
        appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
        serializer = self.get_serializer(appointment)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Appointment Details"
        )
        return response.send(200)

    def put(self, request, *args, **kwargs):
        appointment_id = self.kwargs.get(self.lookup_field)
        appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
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
        appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
        appointment.delete()
        response = PrepareResponse(
            success=True,
            message="Appointment deleted successfully"
        )
        return response.send(204)
    
class AppointmentSlotListAPIView(generics.ListAPIView):
    queryset = AppointmentSlot.objects.all()
    serializer_class = AppointmentSlotSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        saloon_id = self.request.query_params.get('saloon_id')
        if saloon_id:
            queryset = queryset.filter(saloon_id=saloon_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = PrepareResponse(
                success=True,
                message="Appointment slots fetched successfully",
                data=serializer.data
            )
            return self.get_paginated_response(response.send())

        serializer = self.get_serializer(queryset, many=True)
        response = PrepareResponse(
            success=True,
            message="Appointment slots fetched successfully",
            data=serializer.data
        )
        return response.send()

class AppointmentSlotCreateAPIView(generics.GenericAPIView):
    queryset = AppointmentSlot.objects.all()
    serializer_class = AppointmentSlotSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        response = PrepareResponse(
            success=True,
            message="Appointment slot created successfully",
            data=serializer.data
        )
        return response.send(status.HTTP_201_CREATED)

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