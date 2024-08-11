from django.urls import path
from .views import SaloonListView, SaloonDetailView, GalleryUploadView, PopularSaloonListView

urlpatterns = [
    path('saloons/', SaloonListView.as_view(), name='saloon-list'),
    path('saloons/<uuid:pk>/', SaloonDetailView.as_view(), name='saloon-detail'),
    path('saloons/upload/', GalleryUploadView.as_view(), name='gallery-upload'),
    path('saloons/popular/', PopularSaloonListView.as_view(), name='popular-saloon-list'),
]
