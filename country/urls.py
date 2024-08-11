from django.urls import path
from .views import CountryListView

urlpatterns = [
    path('list/', CountryListView.as_view(), name='country_list'),
]