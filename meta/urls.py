from django.urls import path
from .views import AboutView, WhoWeAreView, PhilosophyView, FAQView, PrivacyPolicyView, TermsAndConditionView

urlpatterns = [
    path('about/', AboutView.as_view(), name='about'),
    path('whoweare/', WhoWeAreView.as_view(), name='whoweare'),
    path('philosophy/', PhilosophyView.as_view(), name='philosophy'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('privacypolicy/', PrivacyPolicyView.as_view(), name='privacypolicy'),
    path('termsandcondition/', TermsAndConditionView.as_view(), name='termsandcondition'),
]