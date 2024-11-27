from django.urls import path
from .views import (
    StatisticsCounterView
)

urlpatterns = [
    path('data/list/', StatisticsCounterView.as_view(), name='statistics_counter'),
]