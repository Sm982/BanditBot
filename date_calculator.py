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
    
    # First try to debug what's being received
    print(f"Input time_type: {time_type}")
    
    # Different pattern to handle various time formats
    if "am" in time_type.lower() or "pm" in time_type.lower():
        am_pm = "am" if "am" in time_type.lower() else "pm"
        # Remove the am/pm suffix to process the numeric part
        numeric_part = time_type.lower().replace(am_pm, "")
        
        # Check the length to determine format
        if len(numeric_part) <= 2:  # Simple format like "7pm"
            hour = int(numeric_part)
            minute = 0
        elif len(numeric_part) == 3:  # Format like "230pm" (2:30 PM)
            hour = int(numeric_part[0])
            minute = int(numeric_part[1:])
        elif len(numeric_part) == 4:  # Format like "1230pm" (12:30 PM)
            hour = int(numeric_part[:2])
            minute = int(numeric_part[2:])
        else:
            raise ValueError(f"Invalid time format: {time_type}")
    else:
        raise ValueError(f"Missing AM/PM indicator: {time_type}")
    
    print(f"Parsed hour: {hour}, minute: {minute}, am_pm: {am_pm}")
    
    # Validate hour before conversion
    if hour < 1 or hour > 12:
        raise ValueError(f"Hour must be between 1 and 12: {hour}")
    
    # Convert to 24-hour format
    if am_pm.lower() == 'pm' and hour != 12:
        hour += 12
    elif am_pm.lower() == 'am' and hour == 12:
        hour = 0
    
    print(f"24-hour format: {hour}:{minute}")
    
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
    
    print(f"Target datetime: {target_datetime}")
    
    # Convert to epoch time (UTC timestamp)
    epoch_time = int(target_datetime.timestamp())
    
    print(f"Epoch time: {epoch_time}")
    return epoch_time