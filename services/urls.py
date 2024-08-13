from django.urls import path
from .views import ServiceCategoryListView, ServiceListView, ServiceDetailView, ServiceImageUploadView

urlpatterns = [
    path('categories/', ServiceCategoryListView.as_view(), name='service-category-list'),
    path('services/<uuid:saloon_id>/', ServiceListView.as_view(), name='service-list'),
    path('services/<uuid:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('services/upload-image/<uuid:salooon_id>/', ServiceImageUploadView.as_view(), name='service-image-upload'),
]
