from django.urls import path
from moreclub.views import (
    SaloonSetupView,
    SaloonDetailUpdateView,
    UserSaloonListView
)

urlpatterns = [
    path ('saloon/setup/',SaloonSetupView.as_view(),name='setup-saloon'),
    path('users/saloon/<str:saloon_id/',SaloonDetailUpdateView.as_view(),name='saloon-details'),
    path('users/saloons/list/',UserSaloonListView.as_view(),name='user_saloon_list')
]