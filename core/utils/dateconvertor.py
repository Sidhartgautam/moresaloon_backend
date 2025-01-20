import pytz
from datetime import datetime, timedelta

def convert_to_timezone(utc_time, timezone):
    target_timezone = pytz.timezone(timezone)
    return utc_time.astimezone(target_timezone)

def convert_to_utc(local_time, timezone):
    target_timezone = pytz.timezone(timezone)
    return target_timezone.localize(local_time).astimezone(pytz.UTC)

def check_slot_overlap(current_start, current_end, booked_slots, date, saloon_timezone):
    """
    Checks if a given time slot overlaps with any booked slots.

    :param current_start: Start time of the slot (offset-aware datetime)
    :param current_end: End time of the slot (offset-aware datetime)
    :param booked_slots: List of tuples [(start_time, end_time), ...]
    :param date: The date for which the slots are being checked
    :param saloon_timezone: The timezone of the saloon
    :return: Boolean indicating overlap
    """
    target_timezone = pytz.timezone(saloon_timezone)
    
    for booked_start, booked_end in booked_slots:
        # Convert booked times to datetime using the same date and saloon timezone
        booked_start_datetime = target_timezone.localize(datetime.combine(date, booked_start))
        booked_end_datetime = target_timezone.localize(datetime.combine(date, booked_end))

        # Check for overlap
        if not (current_end <= booked_start_datetime or current_start >= booked_end_datetime):
            return True
    return False
