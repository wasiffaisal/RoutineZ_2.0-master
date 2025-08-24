from datetime import datetime
import re
from .config import BD_TIMEZONE
from .utils import debugprint

class TimeUtils:
    @staticmethod
    def convert_to_bd_time(time_str):
        """Convert time string to Bangladesh timezone."""
        debugprint(f"Converting time to Bangladesh timezone: {time_str}")
        try:
            time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
            dt = datetime.now().replace(
                hour=time_obj.hour,
                minute=time_obj.minute,
                second=time_obj.second,
                microsecond=0,
            )
            bd_dt = BD_TIMEZONE.localize(dt)
            result = bd_dt.strftime("%H:%M:%S")
            debugprint(f"Converted {time_str} to Bangladesh time: {result}")
            return result
        except Exception as e:
            debugprint(f"Error converting time to Bangladesh timezone: {e}")
            return time_str

    @staticmethod
    def time_to_minutes(tstr):
        """Convert time string to minutes (handles both 24-hour and 12-hour formats)."""
        if not tstr:
            debugprint(f"Warning: Empty time string")
            return 0

        tstr = tstr.strip().upper()
        debugprint(f"Converting time to minutes: {tstr}")

        try:
            if "AM" in tstr or "PM" in tstr:
                if ":" not in tstr:
                    tstr = tstr.replace(" ", ":00 ")
                tstr = re.sub(r":\d+\s*(AM|PM)", r" \1", tstr)
                try:
                    dt = datetime.strptime(tstr, "%I:%M %p")
                    minutes = dt.hour * 60 + dt.minute
                    debugprint(f"Converted {tstr} to {minutes} minutes (12-hour format)")
                    return minutes
                except ValueError:
                    try:
                        dt = datetime.strptime(tstr, "%I %p")
                        minutes = dt.hour * 60 + dt.minute
                        debugprint(f"Converted {tstr} to {minutes} minutes (12-hour short format)")
                        return minutes
                    except ValueError:
                        debugprint(f"Warning: Could not parse time string: {tstr}")
                        return 0
            else:
                try:
                    dt = datetime.strptime(tstr, "%H:%M:%S")
                    minutes = dt.hour * 60 + dt.minute
                    debugprint(f"Converted {tstr} to {minutes} minutes (24-hour format)")
                    return minutes
                except ValueError:
                    try:
                        dt = datetime.strptime(tstr, "%H:%M")
                        minutes = dt.hour * 60 + dt.minute
                        debugprint(f"Converted {tstr} to {minutes} minutes (24-hour short format)")
                        return minutes
                    except ValueError:
                        debugprint(f"Warning: Could not parse time string: {tstr}")
                        return 0

        except Exception as e:
            debugprint(f"Error converting time to minutes: {e}")
            return 0

    @staticmethod
    def minutes_to_time(minutes):
        """Convert minutes to time string in 24-hour format (HH:MM:SS)."""
        try:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours:02d}:{mins:02d}:00"
        except Exception as e:
            debugprint(f"Error converting minutes to time: {e}")
            return "00:00:00"

def parse_time(tstr):
    """Parse time string to datetime object."""
    debugprint(f"Parsing time string: {tstr}")
    try:
        result = datetime.strptime(tstr, "%I:%M %p")
        debugprint(f"Parsed {tstr} to datetime object")
        return result
    except Exception as e:
        debugprint(f"Error parsing time string: {e}")
        return None

def slot_to_minutes(slot):
    """Convert time slot to minutes."""
    debugprint(f"Converting time slot to minutes: {slot}")
    try:
        start_str, end_str = slot.split("-")
        start = parse_time(start_str.strip())
        end = parse_time(end_str.strip())
        if start is None or end is None:
            debugprint("Failed to parse start or end time")
            return 0, 0
        start_minutes = start.hour * 60 + start.minute
        end_minutes = end.hour * 60 + end.minute
        debugprint(f"Converted {slot} to minutes: {start_minutes}-{end_minutes}")
        return start_minutes, end_minutes
    except Exception as e:
        debugprint(f"Error converting time slot to minutes: {e}")
        return 0, 0