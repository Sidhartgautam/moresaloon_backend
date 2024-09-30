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
    ServiceVariationListCreateView,
    ServiceVariationDetailUpdateView,
    WorkingDayListCreateView,
    AppointmentSlotListCreateView,
    AppointmentSlotDetailUpdateDeleteView,
    SaloonGalleryListCreateView,
    SaloonGalleryDetailUpdateView

)

urlpatterns = [
    ###############################saloon##################################################################
    path ('saloon/setup/',SaloonSetupView.as_view(),name='setup-saloon'),
    path('users/saloon/<uuid:saloon_id>/',SaloonDetailUpdateView.as_view(),name='saloon-details'),
    path('users/saloons/list/',UserSaloonListView.as_view(),name='user_saloon_list'),

    #############################service##########################################
    path('users/saloons/<uuid:saloon_id>/services/', ServiceListCreateView.as_view(), name='service-list-create'),
    path('users/saloons/<uuid:saloon_id>/services/<uuid:pk>/', ServiceDetailUpdateDeleteView.as_view(), name='service-detail'),

    #####################################serviceVariation###############################################
    path('users/saloons/<uuid:saloon_id>/services/<uuid:service_id>/variations/', ServiceVariationListCreateView.as_view(), name='service-variation-list-create'),
    path('users/saloons/<uuid:saloon_id>/services/<uuid:service_id>/variations/<uuid:service_variation_id>/', ServiceVariationDetailUpdateView.as_view(), name='service-variation-detail'),


    #################################Staff Details################################################
    path('users/saloons/<uuid:saloon_id>/staff/', StaffCreateView.as_view(), name='staff-create'),
    path('users/saloons/<uuid:saloon_id>/staff/<uuid:staff_id>/', StaffDetailUpdateDeleteView.as_view(), name='staff-detail-update-delete'),
    path('users/saloons/<uuid:saloon_id>/staff/<int:staff_id>/slots/', AppointmentSlotListCreateView.as_view(), name='staff_slots'),
    path('users/saloons/<uuid:saloon_id>/staff/<int:staff_id>/slots/<int:slot_id>/', AppointmentSlotDetailUpdateDeleteView.as_view(), name='staff_slot_detail_update_delete'),

    #################################Working Days################################################
    path('users/saloons/<uuid:saloon_id>/staff/<uuid:staff_id>/working-days/', WorkingDayListCreateView.as_view(), name='working-day-list-create'),
    path('users/saloons/<uuid:saloon_id>/staff/<uuid:staff_id>/working-days/detail/', WorkingDayDetailUpdateDeleteView.as_view(), name='working-day-detail-update-delete'),


    #####################################Opening Hours##################################################
    path('users/saloons/<uuid:saloon_id>/opening/hours/', OpeningHourListCreateView.as_view(), name='opening-hour-list-create'),

    ##############################################Gallery################################################
    path('users/saloons/<uuid:saloon_id>/gallery/', SaloonGalleryListCreateView.as_view(), name='saloon-gallery-list-create'),
    path('users/saloons/<uuid:saloon_id>/gallery/<uuid:gallery_id>/', SaloonGalleryDetailUpdateView.as_view(), name='saloon-gallery-detail-update-delete'),

    ##########################################################AppointmentSlot####################################################
    path('users/saloons/<uuid:saloon_id>/staff/<uuid:staff_id>/appointment/slots/', AppointmentSlotListCreateView.as_view(), name='appointment-sloat-list-create'),
    path('users/saloons/<uuid:saloon_id>/staff/<uuid:staff_id>/appointment/slots/<int:slot_id>/', AppointmentSlotDetailUpdateDeleteView.as_view(), name='appointment-sloat-detail-update-delete'),
]