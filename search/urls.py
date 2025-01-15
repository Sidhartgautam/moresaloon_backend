from django.urls import path
from .views import SearchView, SimilarTermsView

urlpatterns = [
    path('search/', SearchView.as_view(), name='saloon_search'),
    path('similar/', SimilarTermsView.as_view(), name='similar_terms'),
]
