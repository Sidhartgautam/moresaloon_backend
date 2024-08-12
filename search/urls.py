from django.urls import path
from .views import SaloonSearchView

urlpatterns = [
    path('search/', SaloonSearchView.as_view(), name='saloon_search'),
]
