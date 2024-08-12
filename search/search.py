from django.db.models import Q, Count
from saloons.models import Saloon
from services.models import Service
from staffs.models import Staff

def search(query=None, category=None, price_min=None, price_max=None, popular_saloons=None):
    # Start with all objects, then filter down
    saloon_results = Saloon.objects.all()
    service_results = Service.objects.all()
    staff_results = Staff.objects.all()

    if query:
        saloon_results = saloon_results.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(address__icontains=query)
        )
        service_results = service_results.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
        staff_results = staff_results.filter(
            Q(name__icontains=query) |
            Q(position__icontains=query)
        )

    if price_min:
        service_results = service_results.filter(price__gte=price_min)

    if price_max:
        service_results = service_results.filter(price__lte=price_max)

    if category:
        service_results = service_results.filter(category__name=category)

    if popular_saloons:
        if popular_saloons == 'popular':
            saloon_results = saloon_results.annotate(review_count=Count('reviews')).order_by('-review_count')
        else:
            saloon_results = saloon_results.annotate(review_count=Count('reviews')).order_by('review_count')

    return {
        'popular_saloons': popular_saloons,
        'saloons': saloon_results,
        'services': service_results,
        'staff': staff_results,
    }
