import datetime
import time
import re

def dateCalculator(day_type, time_type):
    """
    Calculate the epoch time for the next occurrence of the specified day and time.
    
    Args:
        day_type (str): Day of the week (monday, tuesday, etc.)
        time_type (str): Time in format like "7pm", "12am", "1230pm", etc.
    
    Returns:
        int: Epoch timestamp for the specified day and time
    """
    # Convert day_type to a day number (0 = Monday, 6 = Sunday)
    days = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }
    target_day = days.get(day_type.lower())
    
    # Parse the time_type to extract hours, minutes, and AM/PM
    # Handle formats like "7pm", "12am", "1230pm", etc.
    time_pattern = re.compile(r'(\d+)(?:(\d{2}))?([ap]m)', re.IGNORECASE)
    match = time_pattern.match(time_type.lower())
    
    if not match:
        raise ValueError(f"Invalid time format: {time_type}")
    
    hour, minute, am_pm = match.groups()
    hour = int(hour)
    minute = int(minute) if minute else 0
    
    # Convert to 24-hour format
    if am_pm.lower() == 'pm' and hour != 12:
        hour += 12
    elif am_pm.lower() == 'am' and hour == 12:
        hour = 0
    
    # Get the current date and time
    now = datetime.datetime.now()
    current_weekday = now.weekday()
    
    # Calculate days to add to reach the target day
    days_ahead = target_day - current_weekday
    if days_ahead <= 0:  # Target day has already occurred this week
        days_ahead += 7
    
    # Create the target datetime
    target_date = now + datetime.timedelta(days=days_ahead)
    target_datetime = datetime.datetime(
        year=target_date.year,
        month=target_date.month,
        day=target_date.day,
        hour=hour,
        minute=minute
    )
    
    # If the target time today is already past, move to next week
    if target_day == current_weekday and target_datetime <= now:
        target_datetime += datetime.timedelta(days=7)
    
    # Convert to epoch time
    epoch_time = int(target_datetime.timestamp())
    
    return epoch_time