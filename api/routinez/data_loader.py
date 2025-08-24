import requests
import json
import time
from .config import DATA_URL
from .utils import debugprint

# Initialize data as None
data = None

def load_data():
    """Load course data from the API with retry logic."""
    try:
        debugprint(f"\n=== Loading Fresh Data from {DATA_URL} ===")
        
        # Add retry logic
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                debugprint(f"Attempt {attempt + 1}/{max_retries}...")
                response = requests.get(DATA_URL, timeout=30)  # Increased timeout
                response.raise_for_status()
                raw_json = response.json()
                
                debugprint(f"Raw response type: {type(raw_json)}")
                
                # Handle both direct list and {data: [...]} formats
                if isinstance(raw_json, dict) and "data" in raw_json:
                    debugprint("Response is a dict with 'data' key")
                    fresh_data = raw_json["data"]
                else:
                    debugprint("Response is a direct list")
                    fresh_data = raw_json  # If it's already a list
                
                if not isinstance(fresh_data, list):
                    debugprint(f"Warning: Expected list data, got {type(fresh_data)}")
                    continue
                
                # Count sections by course
                course_counts = {}
                for section in fresh_data:
                    course = section.get("courseCode")
                    if course:
                        course_counts[course] = course_counts.get(course, 0) + 1
                
                debugprint(f"Successfully loaded {len(fresh_data)} total sections")
                debugprint("Sections per course:")
                for course, count in sorted(course_counts.items()):
                    debugprint(f"  {course}: {count} sections")
                
                return fresh_data
            except requests.exceptions.RequestException as e:
                debugprint(f"Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    time.sleep(retry_delay)
            except json.JSONDecodeError as e:
                debugprint(f"JSON decode error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        debugprint("All retry attempts failed")
        return None
    except Exception as e:
        debugprint(f"Critical error in load_data: {e}")
        return None