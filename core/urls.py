from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

url_patterns = [
    path('admin/', admin.site.urls),
    path("docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path('api/', include('core.api_urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

urlpatterns = static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + url_patterns