import datetime
import pytz
import time
import re
from logger import logger

def dateCalculator(day_type, time_type):
    """
    Calculate epoch time based on day and time selection.
    
    Args:
        day_type (str): Day of the week (e.g., "monday", "tuesday")
        time_type (str): Time in format like "1230pm", "8am", "11pm"
    
    Returns:
        int: Epoch timestamp for the specified day and time
    """
    # Initialize timezone
    timezone = pytz.timezone("Australia/Brisbane")
    today = datetime.datetime.now(timezone).date()
    
    # Parse the time string
    # Extract hours, minutes, and AM/PM
    time_pattern = re.compile(r'(\d+)(?::?(\d+))?([ap]m)', re.IGNORECASE)
    match = time_pattern.match(time_type)
    
    if not match:
        logger.error(f"Invalid time format: {time_type}")
        return 0
    
    hours = int(match.group(1))
    # If minutes are specified, use them; otherwise, use 0
    minutes = int(match.group(2)) if match.group(2) else 0
    am_pm = match.group(3).lower()
    
    # Convert hours to 24-hour format
    if am_pm == "pm" and hours != 12:
        hours += 12
    elif am_pm == "am" and hours == 12:
        hours = 0
    
    # Map day name to day index (0 = Monday, 6 = Sunday)
    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    try:
        target_day_index = days_of_week.index(day_type.lower())
    except ValueError:
        logger.error(f"Invalid day: {day_type}")
        return 0
    
    # Calculate days until target day
    today_index = today.weekday()  # 0 = Monday, 6 = Sunday
    days_until_next = (target_day_index - today_index) % 7
    
    # If the event is today and the specified time has already passed,
    # schedule it for next week
    if days_until_next == 0:
        current_time = datetime.datetime.now(timezone)
        if (hours > current_time.hour or 
            (hours == current_time.hour and minutes > current_time.minute)):
            # Today but later
            next_day_date = today
        else:
            # Next week
            next_day_date = today + datetime.timedelta(days=7)
    else:
        next_day_date = today + datetime.timedelta(days=days_until_next)
    
    # Create datetime object for the event
    dt = datetime.datetime(
        next_day_date.year,
        next_day_date.month,
        next_day_date.day,
        hours,
        minutes,
        tzinfo=timezone
    )
    
    # Convert to epoch time
    epoch = int(dt.timestamp())
    
    logger.info(f'Calculated epoch time as {epoch} for day: {day_type}, time: {time_type}')
    return epoch