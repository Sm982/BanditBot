import datetime
import time
import re
import pytz

def dateCalculator(day_type, time_type):
    # Set Brisbane timezone
    brisbane_tz = pytz.timezone('Australia/Brisbane')
    
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
    
    # Validate hour before conversion
    if hour < 1 or hour > 12:
        raise ValueError(f"Hour must be between 1 and 12: {hour}")
    
    # Convert to 24-hour format
    if am_pm.lower() == 'pm' and hour != 12:
        hour += 12
    elif am_pm.lower() == 'am' and hour == 12:
        hour = 0
    
    # Double-check hour is now valid for datetime (0-23)
    if hour < 0 or hour > 23:
        raise ValueError(f"Converted hour must be between 0 and 23: {hour}")
    
    # Get the current date and time in Brisbane timezone
    now = datetime.datetime.now(brisbane_tz)
    current_weekday = now.weekday()
    
    # Calculate days to add to reach the target day
    days_ahead = target_day - current_weekday
    if days_ahead < 0:  # Target day has already occurred this week
        days_ahead += 7
    elif days_ahead == 0:  # Today is the target day
        # Create a datetime for today with the target hour and minute
        today_target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        # If target time is already past, schedule for next week
        if today_target <= now:
            days_ahead = 7
    
    # Create the target datetime
    target_date = now + datetime.timedelta(days=days_ahead)
    target_datetime = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Convert to epoch time (UTC timestamp)
    epoch_time = int(target_datetime.timestamp())
    
    return epoch_time