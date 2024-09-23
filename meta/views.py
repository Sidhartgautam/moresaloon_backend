from rest_framework import generics
from .models import About, WhoWeAre, Philosophy, FAQ, PrivacyPolicy, TermsAndCondition
from .serializers import AboutSerializer, WhoWeAreSerializer, PhilosophySerializer, FAQSerializer, PrivacyPolicySerializer, TermsAndConditionSerializer
from core.utils.response import PrepareResponse
# Create your views here.

class AboutView(generics.GenericAPIView):
    serializer_class = AboutSerializer    
    def get(self, request, *args, **kwargs):
        about_detail = About.objects.all()
        serializer = self.serializer_class(about_detail, many=True)
        
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="About retrieved successfully"
        )
        return response.send(200)
    
class WhoWeAreView(generics.GenericAPIView):
    serializer_class = WhoWeAreSerializer
    def get(self, request, *args, **kwargs):
        who_we_are = WhoWeAre.objects.all()
        serializer = self.serializer_class(who_we_are, many=True)
        
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Who We Are retrieved successfully"
        )
        return response.send(200)
    
class PhilosophyView(generics.GenericAPIView):
    serializer_class = PhilosophySerializer
    def get(self, request, *args, **kwargs):
        philosophy = Philosophy.objects.all()
        serializer = self.serializer_class(philosophy, many=True)
        
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Philosophy retrieved successfully"
        )
        return response.send(200)
    
class FAQView(generics.GenericAPIView):
    serializer_class = FAQSerializer
    
    def get(self, request, *args, **kwargs):
        faq = FAQ.objects.all()
        serializer = self.serializer_class(faq, many=True)
        
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="FAQ retrieved successfully"
        )
        return response.send(200)
    
class PrivacyPolicyView(generics.GenericAPIView):
    serializer_class = PrivacyPolicySerializer
    
    def get(self, request, *args, **kwargs):
        privacy_policy = PrivacyPolicy.objects.all()
        serializer = self.serializer_class(privacy_policy, many=True)
        
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Privacy Policy retrieved successfully"
        )
        return response.send(200)
    
class TermsAndConditionView(generics.GenericAPIView):
    serializer_class = TermsAndConditionSerializer
    
    def get(self, request, *args, **kwargs):
        terms_and_condition = TermsAndCondition.objects.all()
        serializer = self.serializer_class(terms_and_condition, many=True)
        
        response = PrepareResponse(
            success=True,
            data=serializer.data,
            message="Terms and Condition retrieved successfully"
        )
        return response.send(200)