from django.urls import path, include

urlpatterns = [
    path('users/', include('users.urls')),
    path('saloons/', include('saloons.urls')),
    path('country/', include('country.urls')),
    path('services/', include('services.urls')), 
    path('search/', include('search.urls')), 
    path('staffs/', include('staffs.urls')),
    path('appointments/', include('appointments.urls')),
    path('reviews/', include('review.urls')),
    path('newsletter/', include('newsletter.urls')),
    path('offers/', include('offers.urls')),
    path ('openinghours/', include('openinghours.urls')),
    path('payments/', include('payments.urls')),
    path('moreclub/',include('moreclub.urls'))
]