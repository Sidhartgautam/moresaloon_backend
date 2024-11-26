# from django.db.models import Q, Count,Avg,OuterRef, Subquery
# from saloons.models import Saloon
# from services.models import Service, ServiceVariation
# from staffs.models import Staff
# from appointments.models import Appointment

# from django.db.models import Q, Count, Avg

# def search(query=None, price_min=None, price_max=None, preferences=None, location=None, country_id=None, sort_price=None,discount_percentage=None, ratings=None):

#     # Initialize results
#     saloon_results = Saloon.objects.none()
#     service_results = Service.objects.none()
#     staff_results = Staff.objects.none()
#     service_variation_results = ServiceVariation.objects.none()
    

#     # Determine if we have relevant parameters for each model
#     has_saloon_params = any([query, location, country_id, preferences, ratings])
#     has_service_params = any([query, price_min, price_max])
#     has_staff_params = any([query, location, country_id])
#     has_service_variation_params = any([price_min, price_max, sort_price, query])
#     if not has_saloon_params and not has_service_params and not has_staff_params and not has_service_variation_params:
#         saloon_results = Saloon.objects.all()
#         service_results = Service.objects.all()
#         staff_results = Staff.objects.all()
#         service_variation_results = ServiceVariation.objects.all()


#     # Search in Saloon
#     if has_saloon_params:
#         saloon_results = Saloon.objects.all()
#         if query:
#             saloon_results = saloon_results.filter(
#                 Q(name__icontains=query) |
#                 Q(short_description__icontains=query) |
#                 Q(long_description__icontains=query) |
#                 Q(address__icontains=query) 
#                 # Q(amenities__icontains=query)
#             )
#         if location:
#             saloon_results = saloon_results.filter(Q(address__icontains=location))
#         if country_id:
#             saloon_results = saloon_results.filter(country_id=country_id)
#         if preferences == 'popular':
#             saloon_results = saloon_results.annotate(appointment_count=Count('appointment')).order_by('-appointment_count')
#         # if amenities:
#         #     if isinstance(amenities, str):
#         #         amenities = [a.strip() for a in amenities.split(',') if a]
#         #     if isinstance(amenities, list):
#         #         saloon_results = saloon_results.filter(amenities__name__in=amenities)
#         if ratings:
#             saloon_results = saloon_results.annotate(average_rating=Avg('reviews__rating')).filter(
#                 average_rating__isnull=False,
#                 average_rating=ratings
#             )

#     # Search in Service
#     if has_service_params:
#         service_results = Service.objects.all()
#         if query:
#             service_results = service_results.filter(
#                 Q(name__icontains=query) |
#                 Q(description__icontains=query)
#             )

#     # Search in Staff
#     if has_staff_params:
#         staff_results = Staff.objects.all()
#         if query:
#             staff_results = staff_results.filter(
#                 Q(name__icontains=query) |
#                 Q(description__icontains=query)
#             )
#         if location:
#             staff_results = staff_results.filter(Q(saloon__address__icontains=location))
#         if country_id:
#             staff_results = staff_results.filter(Q(saloon__country_id=country_id))

#     # Search in Service Variation
#     if has_service_variation_params:
#         service_variation_results = ServiceVariation.objects.all()
#         if query:
#             service_variation_results = service_variation_results.filter(
#                 Q(name__icontains=query) |
#                 Q(description__icontains=query)
#             )
#         if price_min:
#             service_variation_results = service_variation_results.filter(price__gte=price_min)
#         if price_max:
#             service_variation_results = service_variation_results.filter(price__lte=price_max)
#         if sort_price == 'low_to_high':
#             service_variation_results = service_variation_results.order_by('price')
#         elif sort_price == 'high_to_low':
#             service_variation_results = service_variation_results.order_by('-price')
#         if discount_percentage:
#             if discount_percentage == 'up_to_10':
#                 service_variation_results = service_variation_results.filter(discount_percentage__lte=10)
#             elif discount_percentage == 'up_to_25':
#                 service_variation_results = service_variation_results.filter(discount_percentage__lte=25)
#             elif discount_percentage == 'up_to_50':
#                 service_variation_results = service_variation_results.filter(discount_percentage__lte=50)
#             elif discount_percentage == 'up_to_75':
#                 service_variation_results = service_variation_results.filter(discount_percentage__lte=75)


#     # Prepare response
#     response = {}
#     if saloon_results.exists():
#         response['saloons'] = saloon_results
#     if service_results.exists():
#         response['services'] = service_results
#     if staff_results.exists():
#         response['staff'] = staff_results
#     if service_variation_results.exists():
#         response['service_variations'] = service_variation_results

#     return response if response else None

from django.db.models import Q, Count,Avg,OuterRef, Subquery
from saloons.models import Saloon
from services.models import Service, ServiceVariation
from staffs.models import Staff
from appointments.models import Appointment
from django.db.models.functions import Coalesce

from django.db.models import Q, Count, Avg
from core.utils.normalize_text import normalize_amenity



def search(query=None, price_min=None, price_max=None, preferences=None, location=None, country_id=None, amenities=None, sort_price=None, discount_percentage=None, ratings=None):

    # Initialize results
    saloon_results = Saloon.objects.none()
    service_results = Service.objects.none()
    staff_results = Staff.objects.none()
    service_variation_results = ServiceVariation.objects.none()

    # Determine if we have relevant parameters for each model
    has_saloon_params = any([query, location, country_id, preferences, amenities, ratings])
    has_service_params = any([query])
    has_staff_params = any([query, location, country_id])
    has_service_variation_params = any([price_min, price_max, sort_price, query, discount_percentage])

    if not has_saloon_params and not has_service_params and not has_staff_params and not has_service_variation_params:
        saloon_results = Saloon.objects.all()
        service_results = Service.objects.all()
        staff_results = Staff.objects.all()
        service_variation_results = ServiceVariation.objects.all()

    # Search in Saloon
    if has_saloon_params:
        saloon_results = Saloon.objects.all() 
        saloon_filters = Q()

        if query:
            saloon_filters |= (Q(name__icontains=query) | Q(short_description__icontains=query) | Q(long_description__icontains=query) | Q(address__icontains=query))
        
        if location:
            saloon_filters &= Q(address__icontains=location)
        
        if country_id:
            saloon_filters &= Q(country_id=country_id)

        if amenities:
            for amenity in amenities:
                normalized_amenity = normalize_amenity(amenity)
                saloon_filters &= Q(amenities__contains=[normalized_amenity])
        
        if ratings:
            saloon_results = saloon_results.annotate(average_rating=Avg('reviews__rating')).filter(average_rating__gte=ratings)
        
        if preferences == 'popular':
            saloon_results = saloon_results.annotate(appointment_count=Count('appointment')).order_by('-appointment_count')
        
        saloon_results = saloon_results.filter(saloon_filters)

    # Search in Service
    if has_service_params:
        service_results = Service.objects.all().only('name', 'description')
        service_filters = Q()
        
        if query:
            service_filters |= (Q(name__icontains=query) | Q(description__icontains=query))
        service_results = service_results.filter(service_filters)

        if location:
            service_filters &= Q(saloon__address__icontains=location)

    # Search in Staff
    if has_staff_params:
        staff_results = Staff.objects.all().select_related('saloon')
        staff_filters = Q()

        if query:
            staff_filters |= (Q(name__icontains=query) | Q(description__icontains=query))
        
        if location:
            staff_filters &= Q(saloon__address__icontains=location)
        
        if country_id:
            staff_filters &= Q(saloon__country_id=country_id)
        
        staff_results = staff_results.filter(staff_filters)

    # Search in Service Variation
    if has_service_variation_params:
        service_variation_results = ServiceVariation.objects.all().only('name', 'description', 'price', 'discount_price')  # Limit fields
        service_variation_filters = Q()

        if query:
            service_variation_filters |= (Q(name__icontains=query) | Q(description__icontains=query))

        if location:
            service_variation_filters &= Q(saloon__address__icontains=location)
        
        if price_min is not None:
            service_variation_filters &= (
                Q(discount_price__gte=price_min) | 
                Q(discount_price__isnull=True, price__gte=price_min)
            )
        
        if price_max is not None:
            service_variation_filters &= (
                Q(discount_price__lte=price_max) | 
                Q(discount_price__isnull=True, price__lte=price_max)
            )
        
        if sort_price == 'low_to_high':
            service_variation_results = service_variation_results.order_by(Coalesce('discount_price', 'price'))
        elif sort_price == 'high_to_low':
            service_variation_results = service_variation_results.order_by('-price')

        service_variation_results = service_variation_results.filter(service_variation_filters)

        # Apply discount filtering after fetching queryset
        if discount_percentage:
            service_variation_results = list(service_variation_results)
            if discount_percentage == 'up_to_10':
                service_variation_results = [
                    sv for sv in service_variation_results if sv.discount_price and ((sv.price - sv.discount_price) / sv.price) * 100 <= 10
                ]
            elif discount_percentage == 'up_to_25':
                service_variation_results = [
                    sv for sv in service_variation_results if sv.discount_price and ((sv.price - sv.discount_price) / sv.price) * 100 <= 25
                ]
            elif discount_percentage == 'up_to_50':
                service_variation_results = [
                    sv for sv in service_variation_results if sv.discount_price and ((sv.price - sv.discount_price) / sv.price) * 100 <= 50
                ]
            elif discount_percentage == 'up_to_75':
                service_variation_results = [
                    sv for sv in service_variation_results if sv.discount_price and ((sv.price - sv.discount_price) / sv.price) * 100 <= 75
                ]

    # Prepare response
    response = {}
    if saloon_results.exists():
        response['saloons'] = saloon_results
    if service_results.exists():
        response['services'] = service_results
    if staff_results.exists():
        response['staff'] = staff_results
    if service_variation_results:
        response['service_variations'] = service_variation_results

    return response if response else None


# from django.db.models import Q, Count, Avg
# from django.db.models.functions import Coalesce
# from saloons.models import Saloon
# from services.models import Service, ServiceVariation
# from staffs.models import Staff

# def search(query=None, price_min=None, price_max=None, preferences=None, location=None, country_id=None, amenities=None, sort_price=None, discount_percentage=None, ratings=None):

#     # Initialize results
#     saloon_results = Saloon.objects.none()
#     service_results = Service.objects.none()
#     staff_results = Staff.objects.none()
#     service_variation_results = ServiceVariation.objects.none()

#     # Determine if we have relevant parameters for each model
#     has_saloon_params = any([query, location, country_id, preferences, amenities, ratings])
#     has_service_params = any([query])
#     has_staff_params = any([query, location, country_id])
#     has_service_variation_params = any([price_min, price_max, sort_price, query, discount_percentage])

#     if not has_saloon_params and not has_service_params and not has_staff_params and not has_service_variation_params:
#         saloon_results = Saloon.objects.all()
#         service_results = Service.objects.all()
#         staff_results = Staff.objects.all()
#         service_variation_results = ServiceVariation.objects.all()

#     # Search in Saloon
#     if has_saloon_params:
#         saloon_results = Saloon.objects.all()
#         saloon_filters = Q()

#         if query:
#             saloon_filters |= (Q(name__icontains=query) | Q(short_description__icontains=query) | Q(long_description__icontains=query) | Q(address__icontains=query))
        
#         if location:
#             saloon_filters &= Q(address__icontains=location)
        
#         if country_id:
#             saloon_filters &= Q(country_id=country_id)
#         if amenities:
#             if isinstance(amenities, str):
#                 amenities = [amenities] 
#             for amenity in amenities:
#                 saloon_filters &= Q(amenities__contains=[amenity])
#         print(amenities)
        
#         if ratings:
#             saloon_results = saloon_results.annotate(average_rating=Avg('reviews__rating')).filter(average_rating__gte=ratings)
        
#         if preferences == 'popular':
#             saloon_results = saloon_results.annotate(appointment_count=Count('appointment')).order_by('-appointment_count')
        
#         saloon_results = saloon_results.filter(saloon_filters)

#     # Ensure services are linked to the saloons found
#     if saloon_results.exists():
#         service_results = Service.objects.filter(saloon__in=saloon_results).distinct()

#     # Search in Staff
#     if has_staff_params:
#         staff_results = Staff.objects.filter(saloon__in=saloon_results).select_related('saloon')  # Filter staff based on the found saloons
    
#         staff_filters = Q()

#         if query:
#             staff_filters |= (Q(name__icontains=query) | Q(description__icontains=query))
        
#         if location:
#             staff_filters &= Q(saloon__address__icontains=location)
        
#         if country_id:
#             staff_filters &= Q(saloon__country_id=country_id)
        
#         staff_results = staff_results.filter(staff_filters)

#     # Ensure service variations are linked to the found services (not saloons)
#     if service_results.exists():
#         service_variation_results = ServiceVariation.objects.filter(service__in=service_results).distinct()

#     # Apply additional filtering for service variations
#     if has_service_variation_params:
#         # Handle price filtering based on either `price` or `discount_price`
#         service_variation_filters = Q()

#         if query:
#             service_variation_filters |= (Q(name__icontains=query) | Q(description__icontains=query))
        
#         if price_min is not None:
#             # Filter where either price or discount_price is greater than or equal to price_min
#             service_variation_filters &= (
#                 Q(discount_price__gte=price_min) | 
#                 Q(discount_price__isnull=True, price__gte=price_min)
#             )
        
#         if price_max is not None:
#             # Filter where either price or discount_price is less than or equal to price_max
#             service_variation_filters &= (
#                 Q(discount_price__lte=price_max) | 
#                 Q(discount_price__isnull=True, price__lte=price_max)
#             )
        
#         service_variation_results = service_variation_results.filter(service_variation_filters)

#         # Sort by price or discount_price (use Coalesce to prioritize discount_price)
#         if sort_price == 'low_to_high':
#             service_variation_results = service_variation_results.order_by(Coalesce('discount_price', 'price'))
#         elif sort_price == 'high_to_low':
#             service_variation_results = service_variation_results.order_by(Coalesce('discount_price', 'price').desc())

#         # Apply discount filtering after fetching queryset
#         if discount_percentage:
#             service_variation_results = list(service_variation_results)
#             if discount_percentage == 'up_to_10':
#                 service_variation_results = [
#                     sv for sv in service_variation_results if sv.discount_price and ((sv.price - sv.discount_price) / sv.price) * 100 <= 10
#                 ]
#             elif discount_percentage == 'up_to_25':
#                 service_variation_results = [
#                     sv for sv in service_variation_results if sv.discount_price and ((sv.price - sv.discount_price) / sv.price) * 100 <= 25
#                 ]
#             elif discount_percentage == 'up_to_50':
#                 service_variation_results = [
#                     sv for sv in service_variation_results if sv.discount_price and ((sv.price - sv.discount_price) / sv.price) * 100 <= 50
#                 ]
#             elif discount_percentage == 'up_to_75':
#                 service_variation_results = [
#                     sv for sv in service_variation_results if sv.discount_price and ((sv.price - sv.discount_price) / sv.price) * 100 <= 75
#                 ]

#     # Prepare response
#     response = {}
#     if saloon_results.exists():
#         response['saloons'] = saloon_results
#     if service_results.exists():
#         response['services'] = service_results
#     if staff_results.exists():
#         response['staff'] = staff_results
#     if service_variation_results.exists():
#         response['service_variations'] = service_variation_results

#     return response if response else None