from django.urls import path
from .views import ReviewListCreateView, ReviewDetailView

urlpatterns = [
    path('saloons/<uuid:saloon_id>/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('saloons/<uuid:saloon_id>/reviews/<uuid:pk>/', ReviewDetailView.as_view(), name='review-detail'),
]
