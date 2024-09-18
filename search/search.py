from django.db.models import Q, Count,Avg,OuterRef, Subquery
from saloons.models import Saloon,Amenities
from services.models import Service, ServiceVariation
from staffs.models import Staff
from appointments.models import Appointment

def search(query=None,  price_min=None, price_max=None, preferences=None, location=None, country_id=None,amenities=None,sort_price=None,ratings=None):
    """
    Search and filter across Saloon, Service, Staff, and ServiceVariation models.
    """
    saloon_results = Saloon.objects.all()
    service_results = Service.objects.all()
    staff_results = Staff.objects.all()
    service_variation_results = ServiceVariation.objects.all()

    # Search in Saloon
    if query:
        saloon_results = saloon_results.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(long_description__icontains=query) |
            Q(address__icontains=query)
        )
        service_results = service_results.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
        service_variation_results = service_variation_results.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(service__name__icontains=query) |
            Q(service__description__icontains=query)
        )

        staff_results = staff_results.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)  

        )
        return{
            'saloons': saloon_results,
            'services': service_results,
            'service_variations': service_variation_results,
            'staff': staff_results
            }
           
    if location:
        saloon_results = saloon_results.filter(
            Q(address__icontains=location)
        )
        service_results = service_results.filter(
            Q(saloon__address__icontains=location)
        )
        staff_results = staff_results.filter(
            Q(saloon__address__icontains=location)
        )

    if country_id:
        saloon_results = saloon_results.filter(country_id=country_id)
        service_results = service_results.filter(saloon__country_id=country_id)
        staff_results = staff_results.filter(saloon__country_id=country_id)
    if price_min:
        service_variation_results = service_variation_results.filter(price__gte=price_min)
        return{
            'service_variations': service_variation_results
        }
    if price_max:
        service_variation_results = service_variation_results.filter(price__lte=price_max)
        return{
            'service_variations': service_variation_results
        }
    if preferences:
        if preferences == 'popular':
            saloon_results = saloon_results.annotate(appointment_count=Count('appointment')).order_by('-appointment_count')
        return {
            'saloons': saloon_results
        }

    if amenities:
        if isinstance(amenities, str):
            amenities = [a.strip() for a in amenities.split(',') if a]
        if isinstance(amenities, list):
            saloon_results = saloon_results.filter(amenities__name__in=amenities)
        return {
            'saloons': saloon_results
        }

    if sort_price == 'low_to_high':
        service_variation_results = service_variation_results.order_by('price')
    elif sort_price == 'high_to_low':
        service_variation_results = service_variation_results.order_by('-price')
        return{
                'service_variations': service_variation_results
    }

    if ratings:
        saloon_results = saloon_results.annotate(average_rating=Avg('reviews__rating')).filter(
            average_rating__isnull=False,
            average_rating=ratings 
        )
        return {
            'saloons': saloon_results
        }
    



    return {
        'saloons': saloon_results,
        'services': service_results,
        'staff': staff_results,
        'service_variations': service_variation_results
    }
