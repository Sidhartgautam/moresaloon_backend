from django.urls import path
from .views import ServiceCategoryListView, ServiceListView, ServiceDetailView, ServiceImageUploadView, ServiceVariationListView, NestedServiceCategoryListView

urlpatterns = [
    path('categories/<uuid:saloon_id>/', ServiceCategoryListView.as_view(), name='service-category-list'),
    path('services/<uuid:saloon_id>/', ServiceListView.as_view(), name='service-list'),
   path('saloon/<uuid:saloon_id>/service/<uuid:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('services/upload-image/<uuid:salooon_id>/', ServiceImageUploadView.as_view(), name='service-image-upload'),
    path('services/variation/<uuid:service_id>/', ServiceVariationListView.as_view(), name='service-variation-list'),
    path('nested-categories/<uuid:saloon_id>/',NestedServiceCategoryListView.as_view(), name='nested-service-category-list'),
]
