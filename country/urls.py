from django.urls import path
from .views import CountryListView,FetchCountryCode


urlpatterns = [
    path('list/', CountryListView.as_view(), name='country_list'),
    path('code/<str:country_code>/', FetchCountryCode.as_view(), name='fetch_country_code'),
]