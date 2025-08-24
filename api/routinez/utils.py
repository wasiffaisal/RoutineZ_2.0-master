from .config import DEBUG

def debugprint(*args, **kwargs):
    """Print debug messages only when DEBUG is True"""
    if DEBUG:
        print(*args, **kwargs)

def normalize_date(date_str):
    """Normalize date string to YYYY-MM-DD format."""
    from datetime import datetime
    
    if not date_str:
        return None
    try:
        # Try parsing common date formats
        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"]:
            try:
                return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None
    except Exception as e:
        debugprint(f"Error normalizing date: {e}")
        return None

def convert_time_24_to_12(text):
    """Helper function to format 24-hour time string to 12-hour AM/PM"""
    import re
    from datetime import datetime
    
    debugprint(f"Converting 24-hour time to 12-hour format: {text}")
    def repl(match):
        t = match.group(0)
        t = t[:5]
        debugprint(f"Processing time match: {t}")
        in_time = datetime.strptime(t, "%H:%M")
        # Use %#I for Windows, %-I for others
        result = in_time.strftime("%#I:%M %p")
        debugprint(f"Converted {t} to {result}")
        return result

    result = re.sub(r"\b([01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?\b", repl, text)
    debugprint(f"Final result: {result}")
    return result

def schedules_overlap(start1, end1, start2, end2):
    """Check if two time ranges overlap."""
    overlap = max(start1, start2) < min(end1, end2)
    debugprint(f"=== STEP 2: Checking Time Conflicts ===")
    debugprint(f"Checking overlap between {start1}-{end1} and {start2}-{end2}: {'Overlap found' if overlap else 'No overlap'}")
    return overlap