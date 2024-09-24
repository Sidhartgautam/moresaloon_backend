from datetime import datetime,date
from django.db import transaction
from django.core.exceptions import ValidationError
from appointments.models import Appointment, AppointmentSlot
from staffs.models import Staff
from services.models import Service, ServiceVariation
from saloons.models import Saloon
from core.utils.response import PrepareResponse
from datetime import datetime, timedelta
from uuid import UUID

def calculate_total_appointment_price(service_variations_uuids):

    total_price = 0

    for variation_uuid in service_variations_uuids:
        try:
            variation = ServiceVariation.objects.get(id=variation_uuid)
            price = variation.discount_price if variation.discount_price else variation.price
            total_price += price
            print("Total Price:", total_price)
        except ServiceVariation.DoesNotExist:
            raise ValueError(f"ServiceVariation with UUID {variation_uuid} does not exist")

    return total_price



def book_appointment(user, saloon_id, staff_id, service_id, slot_id, service_variation_ids,total_price):
    try:
        # Fetch the saloon, staff, service, and slot
        saloon = Saloon.objects.get(id=saloon_id)
        staff = Staff.objects.get(id=staff_id, saloon=saloon)
        service = Service.objects.get(id=service_id, saloon=saloon)
        slot = AppointmentSlot.objects.get(id=slot_id, staff=staff, is_available=True)
    except (Saloon.DoesNotExist, Staff.DoesNotExist, Service.DoesNotExist, AppointmentSlot.DoesNotExist):
        return PrepareResponse(
            success=False,
            data={},
            message="Invalid saloon, staff, service, or slot."
        ).send(400)

    service_variations = ServiceVariation.objects.filter(id__in=service_variation_ids, service=service)
    if service_variations.count() != len(service_variation_ids):
        raise ServiceVariation.DoesNotExist("One or more selected service variations are invalid.")
    for sv in service_variations:
        print("Service Variation:", sv.id)
    

    total_duration = timedelta()
    for variation in service_variations:
        total_duration += variation.duration

    appointment_start_time = datetime.combine(slot.date, slot.start_time)
    appointment_end_time = appointment_start_time + total_duration

    slot_end_datetime = datetime.combine(slot.date, slot.end_time)
    if appointment_end_time > slot_end_datetime:
        return PrepareResponse(
            success=False,
            data={},
            message="The selected slot is not available for the selected service."
        ).send(400)

    overlapping_appointments = Appointment.objects.filter(
        staff=staff,
        start_time__lt=appointment_end_time.time(),
        end_time__gt=appointment_start_time.time()
    )
    if overlapping_appointments.exists():
        return PrepareResponse(
            success=False,
            data={},
            message="The staff is not available during the selected slot."
        ).send(400)

    total_price = calculate_total_appointment_price(service_variation_ids)

    



    return True

# def calculate_appointment_end_time(date, start_time, service_variations_ids, buffer_time=timedelta(minutes=10)):
#     total_duration = timedelta()
#     if not service_variations_ids:
#         raise ValueError("Service variations are required to calculate the appointment duration.")
    
#     service_variations = ServiceVariation.objects.filter(id__in=service_variations_ids)
#     for variation in service_variations:
#         if hasattr(variation, 'duration'):
#             duration = variation.duration
#             if not isinstance(duration, timedelta):
#                 raise ValueError(f"Service variation {variation.id} has an invalid duration type: {type(duration)}")
#             total_duration += duration
#         else:
#             raise ValueError(f"Service variation {variation.id} has no duration.")
#     start_datetime = datetime.combine(date, start_time)
#     end_datetime = start_datetime + total_duration + buffer_time
#     return end_datetime.time()

def calculate_appointment_end_time(date, start_time, service_variations_ids, buffer_time=timedelta(minutes=10)):
    total_duration = timedelta()
    if not service_variations_ids:
        raise ValueError("Service variations are required to calculate the appointment duration.")
    service_variations = ServiceVariation.objects.filter(id__in=service_variations_ids)
    for variation in service_variations:
        if hasattr(variation, 'duration'):
            if isinstance(variation.duration, str):
                hours, minutes, seconds = map(int, variation.duration.split(':'))
                duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            else:
                duration = variation.duration
            if not isinstance(duration, timedelta):
                raise ValueError(f"Service variation {variation.id} has an invalid duration type: {type(duration)}")
            total_duration += duration
        else:
            raise ValueError(f"Service variation {variation.id} has no duration.")
    start_datetime = datetime.combine(date, start_time)
    end_datetime = start_datetime + total_duration + buffer_time
    return end_datetime.time()
 