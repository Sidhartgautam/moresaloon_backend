import json
import stripe
from django.conf import settings
from django.http import JsonResponse
from rest_framework import generics
from core.utils.appointment import calculate_total_appointment_price
import requests


stripe.api_key = settings.STRIPE_SECRET_KEY

# class CreatePaymentIntentView(generics.GenericAPIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             data = json.loads(request.body)
#             currency = data.get('currency', 'usd')
#             payment_method = data.get('payment_method')
#             total_price = calculate_total_appointment_price(data['service_variations_uuids'])

#             # Create a Stripe PaymentIntent
#             payment_intent = stripe.PaymentIntent.create(
#                 amount=int(total_price * 100),  # Amount in cents
#                 currency=currency,
#                 payment_method=payment_method,
#                 confirm=True  # Automatically confirm the payment
#             )

#             return JsonResponse({
#                 'client_secret': payment_intent.client_secret
#             })
        
#         except stripe.error.CardError as e:
#             return JsonResponse({'error': str(e)}, status=400)
#         except stripe.error.StripeError as e:
#             return JsonResponse({'error': str(e)}, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

class CreatePaymentIntentView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            currency = data.get('currency', 'usd')
            payment_method = data.get('payment_method')
            service_variations_uuids = data.get('service_variations_uuids', [])
            
            total_price = calculate_total_appointment_price(service_variations_uuids)

            payment_data = {
                'currency': currency,
                'payment_method': payment_method,
                'price': total_price  
            }
            url = "https://moretrek.com/api/payments/all/stripe/create-payment-intent/"
            response = requests.post(
                url,
                json=payment_data, 
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                payment_response = response.json()
                return JsonResponse(payment_response)
            else:
                return JsonResponse({'error': 'Failed to create payment intent', 'details': response.json()}, status=403)
        
        except Exception as e:
            # Log and return any other errors
            return JsonResponse({'error': str(e)}, status=500)