from datetime import datetime, timedelta
from django.utils import timezone
from appointments.models import Appointment
from services.models import ServiceVariation
from core.utils.dateconvertor import convert_to_utc, convert_to_timezone, check_slot_overlap

def fetch_available_slots(saloon, staff, date, service_variations):
    saloon_timezone = saloon.timezone
    print(f"DEBUG: Saloon Timezone: {saloon_timezone}")

    # Fetch booked appointments as (start_time, end_time)
    booked_appointments = Appointment.objects.filter(
        staff=staff,
        date=date
    ).values_list('start_time', 'end_time')

    print(f"DEBUG: Booked Appointments: {list(booked_appointments)}")

    # Calculate total service duration
    total_duration = timedelta()
    for variation_id in service_variations:
        try:
            variation = ServiceVariation.objects.get(id=variation_id)
            total_duration += variation.duration
            print(f"DEBUG: Service Variation {variation.name}, Duration: {variation.duration}")
        except ServiceVariation.DoesNotExist:
            print(f"DEBUG: Service Variation {variation_id} does not exist.")
            return []

    print(f"DEBUG: Total Service Duration: {total_duration}")

    # Fetch staff working hours for the day
    working_day = staff.working_days.filter(day_of_week=date.strftime("%A")).first()
    if not working_day:
        print(f"DEBUG: No working day found for {date.strftime('%A')}")
        return []

    if not working_day.start_time or not working_day.end_time:
        print(f"DEBUG: Working day found but missing start or end time. Start: {working_day.start_time}, End: {working_day.end_time}")
        return []

    print(f"DEBUG: Working Hours: Start - {working_day.start_time}, End - {working_day.end_time}")

    # Convert working hours to UTC
    working_start_utc = convert_to_utc(
        datetime.combine(date, working_day.start_time), saloon_timezone
    )
    working_end_utc = convert_to_utc(
        datetime.combine(date, working_day.end_time), saloon_timezone
    )

    print(f"DEBUG: Working Hours in UTC: Start - {working_start_utc}, End - {working_end_utc}")

    slots = []
    current_start = working_start_utc
    buffer_time = staff.buffer_time or timedelta(minutes=10)

    print(f"DEBUG: Buffer Time: {buffer_time}")

    while current_start + total_duration + buffer_time <= working_end_utc:
        current_end = current_start + total_duration  # Slot end is service duration from the start

        # Check if the slot overlaps with booked appointments
        if not check_slot_overlap(current_start, current_end, booked_appointments, date, saloon_timezone):
            slots.append({
                "start_time": convert_to_timezone(current_start, saloon_timezone).strftime("%H:%M"),
                "end_time": convert_to_timezone(current_end, saloon_timezone).strftime("%H:%M"),
            })

        # Increment start by service duration + buffer time to avoid overlap
        current_start = current_end + buffer_time

    print(f"DEBUG: Calculated Slots: {slots}")
    return slots