from django.db.models import Q, Count,Avg,OuterRef, Subquery
from saloons.models import Saloon,Amenities
from services.models import Service, ServiceVariation
from staffs.models import Staff
from appointments.models import Appointment

from django.db.models import Q, Count, Avg

def search(query=None, price_min=None, price_max=None, preferences=None, location=None, country_id=None, amenities=None, sort_price=None, ratings=None):
    """
    Search and filter across Saloon, Service, Staff, and ServiceVariation models.
    """

    # Initialize results
    saloon_results = Saloon.objects.none()
    service_results = Service.objects.none()
    staff_results = Staff.objects.none()
    service_variation_results = ServiceVariation.objects.none()
    

    # Determine if we have relevant parameters for each model
    has_saloon_params = any([query, location, country_id, preferences, amenities, ratings])
    has_service_params = any([query, price_min, price_max])
    has_staff_params = any([query, location, country_id])
    has_service_variation_params = any([price_min, price_max, sort_price, query])
    if not has_saloon_params and not has_service_params and not has_staff_params and not has_service_variation_params:
        saloon_results = Saloon.objects.all()
        service_results = Service.objects.all()
        staff_results = Staff.objects.all()
        service_variation_results = ServiceVariation.objects.all()


    # Search in Saloon
    if has_saloon_params:
        saloon_results = Saloon.objects.all()
        if query:
            saloon_results = saloon_results.filter(
                Q(name__icontains=query) |
                Q(short_description__icontains=query) |
                Q(long_description__icontains=query) |
                Q(address__icontains=query)
            )
        if location:
            saloon_results = saloon_results.filter(Q(address__icontains=location))
        if country_id:
            saloon_results = saloon_results.filter(country_id=country_id)
        if preferences == 'popular':
            saloon_results = saloon_results.annotate(appointment_count=Count('appointment')).order_by('-appointment_count')
        if amenities:
            if isinstance(amenities, str):
                amenities = [a.strip() for a in amenities.split(',') if a]
            if isinstance(amenities, list):
                saloon_results = saloon_results.filter(amenities__name__in=amenities)
        if ratings:
            saloon_results = saloon_results.annotate(average_rating=Avg('reviews__rating')).filter(
                average_rating__isnull=False,
                average_rating=ratings
            )

    # Search in Service
    if has_service_params:
        service_results = Service.objects.all()
        if query:
            service_results = service_results.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )

    # Search in Staff
    if has_staff_params:
        staff_results = Staff.objects.all()
        if query:
            staff_results = staff_results.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
        if location:
            staff_results = staff_results.filter(Q(saloon__address__icontains=location))
        if country_id:
            staff_results = staff_results.filter(Q(saloon__country_id=country_id))

    # Search in Service Variation
    if has_service_variation_params:
        service_variation_results = ServiceVariation.objects.all()
        if query:
            service_variation_results = service_variation_results.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
        if price_min:
            service_variation_results = service_variation_results.filter(price__gte=price_min)
        if price_max:
            service_variation_results = service_variation_results.filter(price__lte=price_max)
        if sort_price == 'low_to_high':
            service_variation_results = service_variation_results.order_by('price')
        elif sort_price == 'high_to_low':
            service_variation_results = service_variation_results.order_by('-price')

    # Prepare response
    response = {}
    if saloon_results.exists():
        response['saloons'] = saloon_results
    if service_results.exists():
        response['services'] = service_results
    if staff_results.exists():
        response['staff'] = staff_results
    if service_variation_results.exists():
        response['service_variations'] = service_variation_results

    return response if response else None

#check it

