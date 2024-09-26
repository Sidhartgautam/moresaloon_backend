from django.urls import path
from moreclub.views import (
    SaloonSetupView,
    SaloonDetailUpdateView,
    UserSaloonListView,
    ServiceListCreateView,
    ServiceDetailUpdateDeleteView,
    StaffDetailUpdateDeleteView,
    WorkingDayDetailUpdateDeleteView,
    StaffCreateView,
    OpeningHourListCreateView,
    OpeningHourDetailUpdateDeleteView

)

urlpatterns = [
    ###############################saloon##################################################################
    path ('saloon/setup/',SaloonSetupView.as_view(),name='setup-saloon'),
    path('users/saloon/<uuid:saloon_id>/',SaloonDetailUpdateView.as_view(),name='saloon-details'),
    path('users/saloons/list/',UserSaloonListView.as_view(),name='user_saloon_list'),

    #############################service and service_variations##########################################
    path('users/saloons/<uuid:saloon_id>/services/', ServiceListCreateView.as_view(), name='service-list-create'),
    path('users/saloons/<uuid:saloon_id>/services/<uuid:pk>/', ServiceDetailUpdateDeleteView.as_view(), name='service-detail'),


    #################################Staff Details################################################
    path('saloon/<uuid:saloon_id>/staff/', StaffCreateView.as_view(), name='staff-create'),
    path('users/staff/<uuid:staff_id>', StaffDetailUpdateDeleteView.as_view(), name='staff-detail-update-delete'),
    path('working-days/<uuid:working_day_id>/', WorkingDayDetailUpdateDeleteView.as_view(), name='working-day-detail-update-delete'),

    #####################################Opening Hours##################################################
    path('saloon/<uuid:saloon_id>/opening-hours/', OpeningHourListCreateView.as_view(), name='opening-hour-list-create'),
    path('saloon/<uuid:saloon_id>/opening-hours/<uuid:opening_hour_id>/', OpeningHourDetailUpdateDeleteView.as_view(), name='opening-hour-detail-update-delete'),

]