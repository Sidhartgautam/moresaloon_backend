from django.urls import path
from .views import ServiceListView, ServiceDetailView, ServiceImageUploadView, ServiceVariationListView, NestedServiceListView, AllServiceListView

urlpatterns = [
    path('services/<uuid:saloon_id>/', ServiceListView.as_view(), name='service-list'),
   path('saloon/<uuid:saloon_id>/service/<uuid:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('services/upload-image/<uuid:salooon_id>/', ServiceImageUploadView.as_view(), name='service-image-upload'),
    path('services/variation/<uuid:service_id>/', ServiceVariationListView.as_view(), name='service-variation-list'),
    path('nested-services/<uuid:saloon_id>/',NestedServiceListView.as_view(), name='nested-service-list'),
    path('all-services/', AllServiceListView.as_view(), name='all_services_list'),
]
