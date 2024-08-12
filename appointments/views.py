import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from core.utils.response import PrepareResponse
from core.utils.moredealstoken import get_moredeals_token
import stripe
from django.conf import settings
from django.core.mail import send_mail
from .models import Appointment
from .serializers import AppointmentSerializer
from saloons.models import Saloon

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

    def list(self, request, *args, **kwargs):
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
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        appointment_id = self.kwargs.get(self.lookup_field)
        appointment = get_object_or_404(Appointment, id=appointment_id)
        serializer = self.get_serializer(appointment)
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Appointment Details"
        )
        return response.send(200)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Appointment updated successfully',
            'data': serializer.data
        })

    def delete(self, request, *args, **kwargs):
        appointment = self.get_object()
        appointment.delete()
        return Response({
            'success': True,
            'message': 'Appointment deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
