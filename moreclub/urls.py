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
    SaloonGalleryDetailUpdateView,
    StaffAppointmentListView,
    SaloonAppointmentListView,
    AppointmentDetailListView,
    SaloonOffersCreateView,
    SaloonOffersListView,
    SaloonOffersDetailView,
    SaloonCouponsCreateView,
    SaloonCouponsListView,
    SaloonCouponsDetailView

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

    #################################################################Appointment################################################################
    path('users/saloons/<uuid:saloon_id>/appointments/', SaloonAppointmentListView.as_view(), name='appointment-saloon-list-create'),
    path('users/saloons/<uuid:saloon_id>/staff/<uuid:staff_id>/appointments/', StaffAppointmentListView.as_view(), name='appointment-staff-list'),
    path('users/saloons/<uuid:saloon_id>/appointments/<uuid:appointment_id>/details/', AppointmentDetailListView.as_view(), name='appointment-detail'),

    ###########################################################Saloon Offers#######################################################
    path('users/saloons/<uuid:saloon_id>/offers/create/', SaloonOffersCreateView.as_view(), name='saloon-offers-create'),
    path('users/saloons/<uuid:saloon_id>/offers/list/', SaloonOffersListView.as_view(), name='saloon-offers-list'),
    path('users/saloons/<uuid:saloon_id>/offers/<uuid:offer_id>/details', SaloonOffersDetailView.as_view(), name='saloon-offer-detail'),

    ###########################################################Saloon Coupons#######################################################
    path('users/saloons/<uuid:saloon_id>/coupons/create/', SaloonCouponsCreateView.as_view(), name='saloon-coupons-create'),
    path('users/saloons/<uuid:saloon_id>/coupons/list/', SaloonCouponsListView.as_view(), name='saloon-coupons-list'),
    path('users/saloons/<uuid:saloon_id>/coupons/<uuid:coupon_id>/details', SaloonCouponsDetailView.as_view(), name='saloon-coupon-detail'),
]
