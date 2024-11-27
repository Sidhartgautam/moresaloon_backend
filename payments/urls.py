from django.urls import path
from .views import CreatePaymentIntentView

urlpatterns = [
    path('stripe/create-payment-intent/', CreatePaymentIntentView.as_view(), name='create_payment_intent'),
]