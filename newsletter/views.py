from rest_framework import generics
from .models import Newsletter
from .serializers import NewsletterSerializer
from core.utils.response import PrepareResponse
from core.utils.mail import send_subscription_confirmation_email

# Create your views here.

class NewsletterView(generics.GenericAPIView):
    serializer_class = NewsletterSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_subscription_confirmation_email(serializer.data['email'])
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Newsletter subscribed successfully"
        )
        return response.send(200)
        