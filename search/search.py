from django.db.models import Q, Count
from saloons.models import Saloon
from services.models import Service, ServiceVariation
from staffs.models import Staff

def search(query=None, category=None, price_min=None, price_max=None, popular_saloons=None):
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

        # Search in Service and ServiceVariation through the Service model
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
            Q(description__icontains=query)  # Assuming staff model has a description field
        )

    # Filter ServiceVariation by price range
    if price_min:
        service_variation_results = service_variation_results.filter(price__gte=price_min)

    if price_max:
        service_variation_results = service_variation_results.filter(price__lte=price_max)

    # Popular Saloon filtering
    if popular_saloons:
        if popular_saloons == 'popular':
            saloon_results = saloon_results.annotate(review_count=Count('reviews')).order_by('-review_count')
        else:
            saloon_results = saloon_results.annotate(review_count=Count('reviews')).order_by('review_count')

    return {
        'saloons': saloon_results,
        'services': service_results,
        'staff': staff_results,
        'service_variations': service_variation_results
    }
