import json
import stripe
from django.conf import settings
from django.http import JsonResponse
from rest_framework import generics
from core.utils.appointment import calculate_total_appointment_price
import requests


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        # try:
            data = json.loads(request.body)
            print("data: ", data)
            currency = data.get('currency', 'usd')
            payment_method = "moresaloon"
            service_variations_uuids = data.get('service_variations_uuids', [])  
            print("service_variations_uuids: ", service_variations_uuids)         
            total_price = calculate_total_appointment_price(service_variations_uuids)

            payment_data = {
                'currency': currency,
                'payment_method': payment_method,
                'price': total_price  
            }
            print("price: ", total_price)
            url = f"https://moretrek.com/api/payments/all/stripe/create-payment-intent/"
            response = requests.post(url, data={
                'currency': currency,
                'payment_method': payment_method,
                'price': total_price
            },
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            })
            if response.status_code == 200:
                payment_response = response.json()
                return JsonResponse(payment_response)
            else:
                return JsonResponse({'error': 'Failed to create payment intent', 'details': response.json()}, status=403)
        