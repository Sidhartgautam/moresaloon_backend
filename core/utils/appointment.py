from datetime import datetime,date
from django.db import transaction
from django.core.exceptions import ValidationError
from appointments.models import Appointment, AppointmentSlot
from staffs.models import Staff
from services.models import Service, ServiceVariation
from saloons.models import Saloon
from core.utils.response import PrepareResponse

def calculate_total_appointment_price(service_variations_uuids):
    """
    Calculate the total price based on service variations.
    """
    total_price = 0

    for variation_uuid in service_variations_uuids:
        try:
            variation = ServiceVariation.objects.get(id=variation_uuid)
            total_price += variation.price if variation.price else 0
        except ServiceVariation.DoesNotExist:
            # Handle the case where a ServiceVariation with the given UUID does not exist
            raise ValueError(f"ServiceVariation with UUID {variation_uuid} does not exist")

    return total_price



def book_appointment(user, saloon_id, staff_id, service_id, slot_id, service_variation_id):
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

    try:
        service_variation = ServiceVariation.objects.get(id=service_variation_id, service=service)
    except ServiceVariation.DoesNotExist:
        return PrepareResponse(
            success=False,
            data={},
            message="Selected service variation is invalid."
        ).send(400)

    service_duration = service_variation.duration 

    appointment_start_time = datetime.combine(slot.date, slot.start_time)
    appointment_end_time = appointment_start_time + service_duration

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

    with transaction.atomic():
        appointment = Appointment.objects.create(
            user=user if user and not user.is_anonymous else None,
            saloon=saloon,
            staff=staff,
            service=service,
            start_time=appointment_start_time.time(),
            end_time=appointment_end_time.time(),
            appointment_slot=slot
        )

        slot.is_available = False
        slot.save()

    return PrepareResponse(
        success=True,
        data={'appointment_id': appointment.id},
        message="Appointment booked successfully."
    ).send(200)
