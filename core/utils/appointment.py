from datetime import timedelta
from django.db import transaction
from django.core.exceptions import ValidationError
from appointments.models import Appointment, AppointmentSlot
from staffs.models import Staff
from services.models import Service, ServiceVariation
from saloons.models import Saloon
def calculate_total_appointment_price(services, service_variations):
    """
    Calculate the total price based on services and service variations.
    """
    total_price = 0
    for variation in service_variations:
        total_price += variation.price  
    return total_price




def book_appointment(user, saloon_id, staff_id, service_id, slot_id):

    try:
        saloon = Saloon.objects.get(id=saloon_id)
        staff = Staff.objects.get(id=staff_id, saloon=saloon)
        service = Service.objects.get(id=service_id, saloon=saloon)
        slot = AppointmentSlot.objects.get(id=slot_id, staff=staff, is_available=True)
    except (Saloon.DoesNotExist, Staff.DoesNotExist, Service.DoesNotExist, AppointmentSlot.DoesNotExist):
        raise ValidationError("Invalid saloon, staff, service, or slot.")

    service_duration = service.base_duration
    if service.variations:
        # If service has variations, you might want to adjust the duration here
        service_duration = max(variation.duration for variation in service.variations.all())
    
    appointment_start_time = slot.start_time
    appointment_end_time = appointment_start_time + timedelta(minutes=service_duration)

    if appointment_end_time > slot.end_time:
        raise ValidationError("The service duration exceeds the available slot time.")

    # Ensure no overlapping appointments for the staff
    overlapping_appointments = Appointment.objects.filter(
        staff=staff,
        start_time__lt=appointment_end_time,
        end_time__gt=appointment_start_time
    )
    if overlapping_appointments.exists():
        raise ValidationError("The staff is not available during the selected slot.")

    with transaction.atomic():
        # Create the appointment
        appointment = Appointment.objects.create(
            user=user,
            saloon=saloon,
            staff=staff,
            service=service,
            start_time=appointment_start_time,
            end_time=appointment_end_time,
            slot=slot
        )

        # Mark the slot as unavailable
        slot.is_available = False
        slot.save()

    return appointment