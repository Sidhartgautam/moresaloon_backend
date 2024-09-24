from django.urls import path
from moreclub.views import (
    SaloonSetupView,
    SaloonDetailUpdateView,
    UserSaloonListView,
    ServiceListCreateView,
    ServiceDetailUpdateDeleteView,
    WorkingDayDetailUpdateDeleteView

)

urlpatterns = [
    ###############################saloon##################################################################
    path ('saloon/setup/',SaloonSetupView.as_view(),name='setup-saloon'),
    path('users/saloon/<uuid:saloon_id/',SaloonDetailUpdateView.as_view(),name='saloon-details'),
    path('users/saloons/list/',UserSaloonListView.as_view(),name='user_saloon_list'),

    #############################service and service_variations##########################################
    path('services/', ServiceListCreateView.as_view(), name='service-list-create'),
    path('services/<uuid:pk>/', ServiceDetailUpdateDeleteView.as_view(), name='service-detail'),

    #################################Staff Details################################################
    path('users/staff/<uuid:staff_id>', ServiceDetailUpdateDeleteView.StaffDetailUpdateDeleteView.as_view(), name='staff-detail-update-delete'),
     path('working-days/<uuid:working_day_id>/', WorkingDayDetailUpdateDeleteView.as_view(), name='working-day-detail-update-delete'),
]