from datetime import timedelta

def get_next_occurrence_of_day(weekday, start_date):
    """
    Given a weekday (0 = Monday, 6 = Sunday), this function returns the next
    occurrence of that day starting from start_date.
    """
    days_ahead = weekday - start_date.weekday()
    if days_ahead < 0:  # Target day already passed this week
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)