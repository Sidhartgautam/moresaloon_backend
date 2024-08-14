from django.urls import path
from .views import ReviewListCreateView, ReviewRetrieveUpdateDestroyView

urlpatterns = [
    path('saloons/<uuid:saloon_id>/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('saloons/<uuid:saloon_id>/reviews/<uuid:pk>/', ReviewRetrieveUpdateDestroyView.as_view(), name='review-detail'),
]
