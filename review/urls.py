from django.urls import path
from .views import ReviewListView, ReviewRetrieveUpdateDestroyView, ReviewCreateView, UserReviewListView


urlpatterns = [
    path('saloons/<uuid:saloon_id>/', ReviewListView.as_view(), name='review-list'),
    path('users/', UserReviewListView.as_view(), name='user-review-list'),
    path('saloons/<uuid:saloon_id>/reviews/', ReviewCreateView.as_view(), name='review-create'),
    path('saloons/<uuid:saloon_id>/reviews/<uuid:pk>/', ReviewRetrieveUpdateDestroyView.as_view(), name='review-detail'),
]
