from django.urls import path
from .views import ServiceCategoryListView, ServiceListView, ServiceDetailView, ServiceImageUploadView

urlpatterns = [
    path('categories/', ServiceCategoryListView.as_view(), name='service-category-list'),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/<uuid:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('services/upload-image/', ServiceImageUploadView.as_view(), name='service-image-upload'),
]
