from django.urls import path
from .views import(
    SaloonCreateView,
     SaloonListView, 
     SaloonDetailView, 
     GalleryUploadView, 
     PopularSaloonListView,
     NearestSaloonView
)

urlpatterns = [
    path('saloons/create/', SaloonCreateView.as_view(), name='saloon-create'),
    path('lists/', SaloonListView.as_view(), name='saloon-list'),
    path('<uuid:saloon_id>/details/', SaloonDetailView.as_view(), name='saloon-detail'),
    path('saloons/upload/', GalleryUploadView.as_view(), name='gallery-upload'),
    path('saloons/popular/', PopularSaloonListView.as_view(), name='popular-saloon-list'),
     path('nearest-saloons/', NearestSaloonView.as_view(), name='nearest-saloons'),
]
