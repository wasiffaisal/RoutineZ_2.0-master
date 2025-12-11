import requests
from flask import Flask, jsonify, request, send_file, abort
from flask_cors import CORS
import re
from datetime import datetime, timezone, timedelta
import json
import pytz
import demjson3
import json as pyjson
import os
from itertools import product
import time
import traceback
import logging
import itertools
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Global debug flag - set to True for development, False for production
DEBUG = False

def debugprint(*args, **kwargs):
    """Print debug messages only when DEBUG is True"""
    if DEBUG:
        print(*args, **kwargs)

debugprint("\n=== Loading Environment Variables ===")
# Debug: Print all environment variables
debugprint("Available environment variables:", list(os.environ.keys()))

# Hardcoded Google API key
GOOGLE_API_KEY = "AIzaSyC0G1uNsSKLgrGh7koSpgx4-sySYHyGoM0"
debugprint("Using hardcoded GOOGLE_API_KEY")
debugprint("✓ GOOGLE_API_KEY is set and has a value")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Disable Flask's default access logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Also disable Flask's request logs
import logging
logging.getLogger('werkzeug').disabled = True

# Configure Gemini API
gemini_configured = False
try:
    debugprint("\n=== Configuring Gemini API ===")
    genai.configure(api_key=GOOGLE_API_KEY)
    debugprint("✓ genai.configure called with API key")
    # Create a single model instance to be reused
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")
    debugprint("✓ GenerativeModel instance created")
    debugprint("Gemini API configured with shared model instance.")
    gemini_configured = True
    debugprint("✓ Gemini API configured successfully")
except ImportError as ie:
    print(f"✗ ImportError configuring Gemini: {ie}")
    print("✗ Warning: google.generativeai package not installed. AI features will be disabled.")
except Exception as e:
    print(f"✗ Failed to configure Gemini API: {str(e)}")
    print(f"Error type: {type(e)}")
    gemini_model = None

def check_ai_availability():
    """Check if AI features are available."""
    debugprint("\n=== Checking AI Availability ===")
    if not GOOGLE_API_KEY:
        debugprint("✗ Google API key not configured")
        return False, "Google API key not configured"
    if not gemini_model:
        debugprint("✗ Gemini API not properly configured")
        return False, "Gemini API not properly configured"
    debugprint("✓ AI features available")
    return True, "AI features available"

@app.route("/api/connapi-status")
def check_connapi_status():
    try:
        # Use a simpler approach - just check if the API is reachable
        response = requests.get("https://connect-api.bd-torrent-optimizer.workers.dev/raw-schedule", timeout=10)
        
        # If we can reach the API, consider it online regardless of content
        if response.status_code == 200:
            return jsonify({
                "status": "online",
                "cached": False,
                "message": "API is online and responding"
            })
        else:
            return jsonify({
                "status": "error",
                "cached": True,
                "error": f"API returned status code {response.status_code}"
            }), 503
    except requests.exceptions.Timeout:
        return jsonify({
            "status": "error",
            "cached": True,
            "error": "Connection timed out. Please try again later."
        }), 503
    except requests.exceptions.RequestException as e:
        print(f"Error checking ConnAPI status: {e}")
        return jsonify({
            "status": "error",
            "cached": True,
            "error": "Unable to connect to the API. Please try again later."
        }), 503
    except Exception as e:
        print(f"Unexpected error checking ConnAPI status: {e}")
        return jsonify({
            "status": "error",
            "cached": True,
            "error": "An unexpected error occurred. Please try again later."
        }), 503

@app.route("/api/test")
def test():
    env_vars = list(os.environ.keys())
    api_key = os.environ.get("GOOGLE_API_KEY")
    return jsonify({
        "status": "ok",
        "environment": {
            "has_api_key": bool(api_key),
            "api_key_length": len(api_key) if api_key else 0,
            "available_vars": env_vars
        }
    })

@app.route("/api/courses")
def get_courses():
    try:
        # Get show_all parameter from query string, default to False
        show_all = request.args.get("show_all", "false").lower() == "true"
        
        data = load_data()  # Load data directly in the route
        if data is None:
            return jsonify({"error": "Failed to load course data. Please try again later."}), 503
            
        courses_data = {}
        for section in data:
            code = section.get("courseCode")
            name = section.get("courseName", code)
            available_seats = section.get("capacity", 0) - section.get("consumedSeat", 0)
            
            # Always process the course and include it in the response
            if code not in courses_data:
                courses_data[code] = {
                    "code": code, 
                    "name": name, 
                    "totalAvailableSeats": 0,
                    "hasAvailableSeats": False  # Add flag to indicate if course has any seats
                }
            # Only add positive available seats to the total
            if section.get("capacity", 0) - section.get("consumedSeat", 0) > 0:
                courses_data[code]["totalAvailableSeats"] += available_seats
                courses_data[code]["hasAvailableSeats"] = True
                
        # No debug prints for ACT201 - removed to clean up logs
        
        # Make sure all courses are properly processed
        # This code ensures all courses from the data are included in the response
        missing_courses = set(section.get("courseCode") for section in data if section.get("courseCode")) - set(courses_data.keys())
        for code in missing_courses:
            sections = [section for section in data if section.get("courseCode") == code]
            if sections:
                # Only count positive available seats
                total_available = sum(max(0, section.get("capacity", 0) - section.get("consumedSeat", 0)) for section in sections)
                courses_data[code] = {
                    "code": code,
                    "name": sections[0].get("courseName", code),
                    "totalAvailableSeats": total_available,
                    "hasAvailableSeats": total_available > 0
                }
        
        # No special handling for ACT201 anymore
                
        courses_list = list(courses_data.values())
        return jsonify(courses_list)
    except Exception as e:
        print(f"Error in /api/courses: {e}")
        return jsonify({"error": "Failed to process courses data. Please try again later."}), 503

@app.route('/api/courses/sse')
def courses_sse():
    """Server-Sent Events endpoint for real-time course updates"""
    def generate():
        # Send initial connection event
        yield f"event: connected\ndata: {json.dumps({'status': 'connected'})}\n\n"
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                time.sleep(3)  # Update every 3 seconds for faster testing
                
                # Reload data
                new_data = load_data()
                if new_data:
                    yield f"event: update\ndata: {json.dumps({'timestamp': str(datetime.now())})}\n\n"
                    yield f"event: update\ndata: {json.dumps({'timestamp': datetime.now().isoformat(), 'data': 'refresh'})}\n\n"
                    
            except GeneratorExit:
                break
            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
                break

    return app.response_class(generate(), mimetype='text/event-stream')


# Initialize data as None
data = None

# SSE clients set
sse_clients = set()

def load_data():
    try:
        DATA_URL = "https://connect-api.bd-torrent-optimizer.workers.dev/raw-schedule"  # Using Vercel deployment
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


# Add at the top of usis.py
BD_TIMEZONE = pytz.timezone("Asia/Dhaka")


# Create TimeUtils class
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


# Create an ExamConflictChecker class
class ExamConflictChecker:
    @staticmethod
    def check_conflicts(sections):
        """Check for conflicts between mid-term and final exams of sections."""
        exam_conflicts = []
        for i, section1 in enumerate(sections):
            for j in range(i + 1, len(sections)):
                section2 = sections[j]
                conflicts = check_exam_conflicts(section1, section2)
                if conflicts:
                    exam_conflicts.extend(conflicts)
        return exam_conflicts

    @staticmethod
    def format_conflict_message(conflicts):
        """Format exam conflicts message in a concise way without repetition."""
        if not conflicts:
            return ""

        # Get unique course pairs with conflicts (excluding self-conflicts)
        conflict_pairs = {}  # Changed to dict to store conflict details
        for conflict in conflicts:
            # Skip self-conflicts
            if conflict["course1"] == conflict["course2"]:
                continue
            # Sort courses to avoid duplicates like (A,B) and (B,A)
            courses = tuple(sorted([conflict["course1"], conflict["course2"]]))

            # Store conflict details by course pair
            if courses not in conflict_pairs:
                conflict_pairs[courses] = {"mid": None, "final": None}

            # Store the first occurrence of each exam type
            if (
                "Mid" in (conflict["type1"], conflict["type2"])
                and not conflict_pairs[courses]["mid"]
            ):
                conflict_pairs[courses]["mid"] = conflict["date"]
            if (
                "Final" in (conflict["type1"], conflict["type2"])
                and not conflict_pairs[courses]["final"]
            ):
                conflict_pairs[courses]["final"] = conflict["date"]

        if not conflict_pairs:
            return ""  # No conflicts after removing self-conflicts

        # Build concise message
        courses_involved = sorted(
            set(course for pair in conflict_pairs.keys() for course in pair)
        )

        message = "Exam Conflicts:\n\n"
        message += "Affected Courses:\n"
        message += ", ".join(courses_involved)

        message += "\n\nConflicting Pairs:\n"
        for courses, details in conflict_pairs.items():
            course1, course2 = courses
            conflicts_info = []
            if details["mid"]:
                conflicts_info.append(f"Mid: {details['mid']}")
            if details["final"]:
                conflicts_info.append(f"Final: {details['final']}")
            message += f"{course1} ⟷ {course2} ({', '.join(conflicts_info)})\n"

        return message.strip()


# Helper function to format 24-hour time string to 12-hour AM/PM
def convert_time_24_to_12(text):
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


# Define your time slots (should match frontend)
TIME_SLOTS = [
    "8:00 AM-9:20 AM",
    "9:30 AM-10:50 AM",
    "11:00 AM-12:20 PM",
    "12:30 PM-1:50 PM",
    "2:00 PM-3:20 PM",
    "3:30 PM-4:50 PM",
    "5:00 PM-6:20 PM",
]


def parse_time(tstr):
    debugprint(f"Parsing time string: {tstr}")
    try:
        result = datetime.strptime(tstr, "%I:%M %p")
        debugprint(f"Parsed {tstr} to datetime object")
        return result
    except Exception as e:
        debugprint(f"Error parsing time string: {e}")
        return None


def slot_to_minutes(slot):
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


def schedules_overlap(start1, end1, start2, end2):
    """Check if two time ranges overlap."""
    overlap = max(start1, start2) < min(end1, end2)
    debugprint(f"=== STEP 2: Checking Time Conflicts ===")
    debugprint(f"Checking overlap between {start1}-{end1} and {start2}-{end2}: {'Overlap found' if overlap else 'No overlap'}")
    return overlap


def normalize_date(date_str):
    """Normalize date string to YYYY-MM-DD format."""
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

def exam_schedules_overlap(exam1, exam2):
    """Check if two exam schedules conflict based on date and time using actual exam durations."""
    try:
        # Convert times to minutes for comparison
        def convert_time(time_str):
            if not isinstance(time_str, str):
                debugprint(f"Warning: Invalid time format: {time_str}")
                return None
                
            # Remove any extra whitespace
            time_str = time_str.strip()
            
            # Try 24-hour format first (HH:MM:SS)
            try:
                if ':' in time_str:
                    parts = time_str.split(':')
                    if len(parts) >= 2:
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        return hours * 60 + minutes
                return None
            except ValueError:
                debugprint(f"Error converting time: {time_str}")
                return None

        # Get dates and times
        date1 = normalize_date(exam1.get("date"))
        date2 = normalize_date(exam2.get("date"))
        
        if not date1 or not date2:
            debugprint("Missing date information")
            return False
        
        if date1 != date2:
            debugprint(f"Different dates: {date1} vs {date2}")
            return False
            
        # Parse start and end times from exam data
        start_time1 = convert_time(exam1.get("startTime", ""))
        end_time1 = convert_time(exam1.get("endTime", ""))
        start_time2 = convert_time(exam2.get("startTime", ""))
        end_time2 = convert_time(exam2.get("endTime", ""))
        
        # Fallback to old method if end times are not available
        if start_time1 is None or start_time2 is None:
            debugprint("Missing start time information")
            return False
            
        if end_time1 is None or end_time2 is None:
            # Fallback to 2-hour duration if end times not provided
            end_time1 = start_time1 + 120
            end_time2 = start_time2 + 120
            debugprint("Using 2-hour default duration")
        
        # Check for overlap using actual exam durations
        overlap = max(start_time1, start_time2) < min(end_time1, end_time2)
        debugprint(f"Checking exam overlap: {start_time1}-{end_time1} vs {start_time2}-{end_time2}: {'Overlap' if overlap else 'No overlap'}")
        return overlap
        
    except Exception as e:
        debugprint(f"Error comparing exam schedules: {e}")
        return False  # Return False to be safe if there's an error


def check_exam_conflicts(section1, section2):
    """Check for exam conflicts between two sections."""
    conflicts = []

    # Skip comparison if sections are the same
    if section1.get("sectionId") == section2.get("sectionId"):
        return []

    # Get exam schedules
    schedule1 = section1.get("sectionSchedule", {})
    schedule2 = section2.get("sectionSchedule", {})

    # Check midterm exam conflicts
    if schedule1.get("midExamDate") and schedule2.get("midExamDate"):
        if normalize_date(schedule1["midExamDate"]) == normalize_date(schedule2["midExamDate"]):
            debugprint(f"\nChecking midterm exam conflict for {schedule1['midExamDate']}:")
            debugprint(f"{section1.get('courseCode')} vs {section2.get('courseCode')}")
            
            exam1 = {
                "date": schedule1["midExamDate"],
                "startTime": schedule1.get("midExamStartTime", "").replace(" ", ""),
                "endTime": schedule1.get("midExamEndTime", "").replace(" ", "")
            }
            exam2 = {
                "date": schedule2["midExamDate"],
                "startTime": schedule2.get("midExamStartTime", "").replace(" ", ""),
                "endTime": schedule2.get("midExamEndTime", "").replace(" ", "")
            }
            
            if exam_schedules_overlap(exam1, exam2):
                conflicts.append({
                    "course1": section1.get("courseCode"),
                    "course2": section2.get("courseCode"),
                    "type1": "Mid",
                    "type2": "Mid",
                    "date": schedule1["midExamDate"],
                    "time1": f"{schedule1.get('midExamStartTime')} - {schedule1.get('midExamEndTime')}",
                    "time2": f"{schedule2.get('midExamStartTime')} - {schedule2.get('midExamEndTime')}"
                })

    # Check final exam conflicts
    if schedule1.get("finalExamDate") and schedule2.get("finalExamDate"):
        if normalize_date(schedule1["finalExamDate"]) == normalize_date(schedule2["finalExamDate"]):
            debugprint(f"\nChecking final exam conflict for {schedule1['finalExamDate']}:")
            debugprint(f"{section1.get('courseCode')} vs {section2.get('courseCode')}")
            
            exam1 = {
                "date": schedule1["finalExamDate"],
                "startTime": schedule1.get("finalExamStartTime", "").replace(" ", ""),
                "endTime": schedule1.get("finalExamEndTime", "").replace(" ", "")
            }
            exam2 = {
                "date": schedule2["finalExamDate"],
                "startTime": schedule2.get("finalExamStartTime", "").replace(" ", ""),
                "endTime": schedule2.get("finalExamEndTime", "").replace(" ", "")
            }
            
            if exam_schedules_overlap(exam1, exam2):
                conflicts.append({
                    "course1": section1.get("courseCode"),
                    "course2": section2.get("courseCode"),
                    "type1": "Final",
                    "type2": "Final",
                    "date": schedule1["finalExamDate"],
                    "time1": f"{schedule1.get('finalExamStartTime')} - {schedule1.get('finalExamEndTime')}",
                    "time2": f"{schedule2.get('finalExamStartTime')} - {schedule2.get('finalExamEndTime')}"
                })

    return conflicts


def has_internal_conflicts(section):
    """Check if a single section has overlapping class or lab schedules."""
    debugprint(f"\nChecking internal conflicts for section {section.get('courseCode')} {section.get('sectionName')}")
    
    # Use a dictionary to group schedules by day for O(1) lookups
    schedules_by_day = {}
    
    if section.get("sectionSchedule") and section["sectionSchedule"].get(
        "classSchedules"
    ):
        debugprint("Processing class schedules")
        for sched in section["sectionSchedule"]["classSchedules"]:
            if sched.get("day") and sched.get("startTime") and sched.get("endTime"):
                day = sched["day"].upper()
                schedule = {
                    "start": TimeUtils.time_to_minutes(sched["startTime"]),
                    "end": TimeUtils.time_to_minutes(sched["endTime"]),
                }
                if day not in schedules_by_day:
                    schedules_by_day[day] = []
                schedules_by_day[day].append(schedule)
                debugprint(f"Added class schedule: {sched['day']} {sched['startTime']}-{sched['endTime']}")

    if section.get("labSchedules"):
        debugprint("Processing lab schedules")
        for lab in get_lab_schedules_flat(section):
            if lab.get("day") and lab.get("startTime") and lab.get("endTime"):
                day = lab["day"].upper()
                schedule = {
                    "start": TimeUtils.time_to_minutes(lab["startTime"]),
                    "end": TimeUtils.time_to_minutes(lab["endTime"]),
                }
                if day not in schedules_by_day:
                    schedules_by_day[day] = []
                schedules_by_day[day].append(schedule)
                debugprint(f"Added lab schedule: {lab['day']} {lab['startTime']}-{lab['endTime']}")

    total_schedules = sum(len(schedules) for schedules in schedules_by_day.values())
    debugprint(f"Found {total_schedules} total schedules")

    # Check for conflicts within each day group - optimized approach
    for day, day_schedules in schedules_by_day.items():
        if len(day_schedules) > 1:
            # Sort schedules by start time for efficient overlap checking
            day_schedules.sort(key=lambda x: x["start"])
            
            # Check for overlaps using the sorted list
            prev_end = day_schedules[0]["end"]
            for i in range(1, len(day_schedules)):
                current_start = day_schedules[i]["start"]
                debugprint(f"Checking overlap for {day}:")
                debugprint(f"Schedule 1: {TimeUtils.minutes_to_time(day_schedules[i-1]['start'])}-{TimeUtils.minutes_to_time(day_schedules[i-1]['end'])}")
                debugprint(f"Schedule 2: {TimeUtils.minutes_to_time(current_start)}-{TimeUtils.minutes_to_time(day_schedules[i]['end'])}")
                
                if current_start < prev_end:
                    debugprint("Found internal conflict!")
                    return True
                
                # Update prev_end to be the maximum end time
                prev_end = max(prev_end, day_schedules[i]["end"])

    debugprint("No internal conflicts found")
    return False


@app.route("/api/course_details")
def course_details():
    data = load_data()
    code = request.args.get("course")
    show_all = request.args.get("show_all", "false").lower() == "true"  # Get show_all parameter
    
    debugprint(f"\n=== Getting Course Details for {code} ===")
    debugprint(f"Show All: {show_all}")
    
    # Get all sections for the course
    all_sections = [section for section in data if section.get("courseCode") == code]
    debugprint(f"Found {len(all_sections)} total sections for {code}")

    # Filter sections based on show_all parameter
    details = []
    for section in all_sections:
        available_seats = section.get("capacity", 0) - section.get("consumedSeat", 0)
        if show_all or section.get("capacity", 0) - section.get("consumedSeat", 0) > 0:  # Include all sections if show_all is true
            # Add available seats information
            section["availableSeats"] = available_seats
            debugprint(f"Including section {section.get('sectionName')} with {available_seats} seats")

            # Add exam information - Prioritize data from sectionSchedule
            section_schedule = section.get("sectionSchedule", {})

            # Midterm Exam
            section["midExamDate"] = section_schedule.get("midExamDate") or section.get(
                "midExamDate"
            )
            section["midExamStartTime"] = section_schedule.get(
                "midExamStartTime"
            ) or section.get("midExamStartTime")
            section["midExamEndTime"] = section_schedule.get(
                "midExamEndTime"
            ) or section.get("midExamEndTime")

            # Final Exam
            section["finalExamDate"] = section_schedule.get(
                "finalExamDate"
            ) or section.get("finalExamDate")
            section["finalExamStartTime"] = section_schedule.get(
                "finalExamStartTime"
            ) or section.get("finalExamStartTime")
            section["finalExamEndTime"] = section_schedule.get(
                "finalExamEndTime"
            ) or section.get("finalExamEndTime")

            # Optional: Add formatted exam times (12-hour AM/PM) using the
            # prioritized times
            if section.get("midExamStartTime") and section.get("midExamEndTime"):
                section["formattedMidExamTime"] = convert_time_24_to_12(
                    f"{section['midExamStartTime']} - {section['midExamEndTime']}"
                )
            else:
                section["formattedMidExamTime"] = None

            if section.get("finalExamStartTime") and section.get("finalExamEndTime"):
                section["formattedFinalExamTime"] = convert_time_24_to_12(
                    f"{section['finalExamStartTime']} - {section['finalExamEndTime']}"
                )
            else:
                section["formattedFinalExamTime"] = None

            # Format schedule information
            if section.get("sectionSchedule"):
                class_schedules = section["sectionSchedule"].get("classSchedules")
                if isinstance(class_schedules, list):
                    for schedule in class_schedules:
                        schedule["formattedTime"] = convert_time_24_to_12(
                            f"{schedule['startTime']} - {schedule['endTime']}"
                        )
                else:
                    # If classSchedules is not a list, skip formatting
                    pass

            # Format lab schedule information
            lab_schedules = section.get("labSchedules")
            if isinstance(lab_schedules, list):
                for schedule in lab_schedules:
                    schedule["formattedTime"] = convert_time_24_to_12(
                        f"{schedule['startTime']} - {schedule['endTime']}"
                    )
            else:
                # If labSchedules is not a list, skip formatting
                pass
                
            # Format prerequisite courses
            prereq = section.get("prerequisiteCourses")
            if prereq and prereq.lower() != "n/a" and prereq != "null":
                # Keep the prerequisite courses as is, already formatted in the data
                pass
            else:
                section["prerequisiteCourses"] = None

            details.append(section)

    debugprint(f"Returning {len(details)} sections")
    return jsonify(details)


@app.route("/api/faculty")
def get_faculty():
    # Get unique faculty names from all sections
    faculty = set()
    for section in data:
        if section.get("faculties"):
            faculty.add(section.get("faculties"))
    return jsonify(list(faculty))


@app.route("/api/faculty_for_courses")
def get_faculty_for_courses():
    course_codes = request.args.get("courses", "").split(",")
    faculty = set()

    # Get faculty for each course
    for code in course_codes:
        sections = [section for section in data if section.get("courseCode") == code]
        for section in sections:
            if section.get("faculties"):
                faculty.add(section.get("faculties"))

    return jsonify(list(faculty))


def get_lab_schedule(section):
    """Extract and format lab schedule information for a section, supporting both array and nested object formats."""
    debugprint(f"\nGetting lab schedule for section {section.get('courseCode')} {section.get('sectionName')}")
    lab_schedules = section.get("labSchedules", [])
    formatted_labs = []

    # If lab_schedules is a dict (new API format), extract classSchedules
    if isinstance(lab_schedules, dict):
        debugprint("Processing lab schedules in new API format (dict with classSchedules)")
        class_schedules = lab_schedules.get("classSchedules", [])
        room = section.get("labRoomName") or lab_schedules.get("room", "TBA")
        for sched in class_schedules:
            day = sched.get("day", "").capitalize()
            start = sched.get("startTime")
            end = sched.get("endTime")
            if start and end:
                sched_start = TimeUtils.time_to_minutes(start)
                sched_end = TimeUtils.time_to_minutes(end)
                formatted_time = convert_time_24_to_12(f"{start} - {end}")
                lab_info = {
                    "day": day,
                    "startTime": start,
                    "endTime": end,
                    "formattedTime": formatted_time,
                    "room": room,
                    "startMinutes": sched_start,
                    "endMinutes": sched_end,
                }
                formatted_labs.append(lab_info)
                debugprint(f"Added lab schedule: {day} {formatted_time} in {room}")
    # If lab_schedules is a list (legacy/expected format)
    elif isinstance(lab_schedules, list):
        debugprint("Processing lab schedules in legacy format (list)")
        for lab in lab_schedules:
            day = lab.get("day", "").capitalize()
            start = lab.get("startTime")
            end = lab.get("endTime")
            room = lab.get("room", section.get("labRoomName", "TBA"))
            if start and end:
                sched_start = TimeUtils.time_to_minutes(start)
                sched_end = TimeUtils.time_to_minutes(end)
                formatted_time = convert_time_24_to_12(f"{start} - {end}")
                lab_info = {
                    "day": day,
                    "startTime": start,
                    "endTime": end,
                    "formattedTime": formatted_time,
                    "room": room,
                    "startMinutes": sched_start,
                    "endMinutes": sched_end,
                }
                formatted_labs.append(lab_info)
                debugprint(f"Added lab schedule: {day} {formatted_time} in {room}")
    # Otherwise, return empty list
    else:
        debugprint(f"Warning: Unrecognized lab schedule format: {type(lab_schedules)}")
    
    debugprint(f"Found {len(formatted_labs)} lab schedules")
    return formatted_labs


def get_lab_schedule_bd(section):
    """Extract and format lab schedule information for a section, converting times to Bangladesh timezone (GMT+6)."""
    debugprint(f"\nGetting Bangladesh timezone lab schedule for section {section.get('courseCode')} {section.get('sectionName')}")
    lab_schedules = section.get("labSchedules", []) or []
    formatted_labs = []
    for lab in lab_schedules:
        day = lab.get("day", "").capitalize()
        start = lab.get("startTime")
        end = lab.get("endTime")
        room = lab.get("room", "TBA")
        if start and end:
            debugprint(f"Converting lab time from UTC to BD: {start} - {end}")
            # Parse as UTC and convert to BD time
            try:
                # Assume input is in HH:MM:SS, treat as naive local time,
                # localize to UTC, then convert
                start_dt = datetime.strptime(start, "%H:%M:%S")
                end_dt = datetime.strptime(end, "%H:%M:%S")
                # Attach today's date for conversion
                today = datetime.now().date()
                start_dt = datetime.combine(today, start_dt.time())
                end_dt = datetime.combine(today, end_dt.time())
                # Localize to UTC, then convert to BD
                start_bd = pytz.utc.localize(start_dt).astimezone(BD_TIMEZONE)
                end_bd = pytz.utc.localize(end_dt).astimezone(BD_TIMEZONE)
                start_str_bd = start_bd.strftime("%H:%M:%S")
                end_str_bd = end_bd.strftime("%H:%M:%S")
                formatted_time = convert_time_24_to_12(f"{start_str_bd} - {end_str_bd}")
                sched_start = TimeUtils.time_to_minutes(start_str_bd)
                sched_end = TimeUtils.time_to_minutes(end_str_bd)
                debugprint(f"Converted to BD time: {start_str_bd} - {end_str_bd}")
            except Exception as e:
                # Fallback: use original times
                debugprint(f"Error converting to BD time: {e}")
                debugprint("Using original times as fallback")
                start_str_bd = start
                end_str_bd = end
                formatted_time = convert_time_24_to_12(f"{start} - {end}")
                sched_start = TimeUtils.time_to_minutes(start)
                sched_end = TimeUtils.time_to_minutes(end)
            lab_info = {
                "day": day,
                "startTime": start_str_bd,
                "endTime": end_str_bd,
                "formattedTime": formatted_time,
                "room": room,
                "startMinutes": sched_start,
                "endMinutes": sched_end,
            }
            formatted_labs.append(lab_info)
            debugprint(f"Added lab schedule: {day} {formatted_time} in {room}")
    
    debugprint(f"Found {len(formatted_labs)} lab schedules")
    return formatted_labs


def check_lab_conflicts(section1, section2):
    """Check if two sections have conflicting lab schedules."""
    debugprint(f"\nChecking lab conflicts between {section1.get('courseCode')} and {section2.get('courseCode')}")
    labs1 = get_lab_schedule(section1)
    labs2 = get_lab_schedule(section2)

    debugprint(f"Found {len(labs1)} labs for {section1.get('courseCode')} and {len(labs2)} labs for {section2.get('courseCode')}")

    for lab1 in labs1:
        for lab2 in labs2:
            if lab1["day"] == lab2["day"]:
                debugprint(f"Checking overlap for {lab1['day']}:")
                debugprint(f"{section1.get('courseCode')}: {lab1['formattedTime']} in {lab1['room']}")
                debugprint(f"{section2.get('courseCode')}: {lab2['formattedTime']} in {lab2['room']}")
                if schedules_overlap(
                    lab1["startMinutes"],
                    lab1["endMinutes"],
                    lab2["startMinutes"],
                    lab2["endMinutes"],
                ):
                    debugprint("Found lab conflict!")
                    return True
                else:
                    debugprint("No overlap found")
    
    debugprint("No lab conflicts found")
    return False


def format_exam_conflicts_message(conflicts):
    """Format exam conflicts message in a concise way without repetition."""
    if not conflicts:
        return ""

    # Get unique course pairs with conflicts (excluding self-conflicts)
    mid_conflicts = {}
    final_conflicts = {}
    courses_involved = set()

    for conflict in conflicts:
        # Skip self-conflicts
        if conflict["course1"] == conflict["course2"]:
            continue

        # Add to courses involved
        courses_involved.add(conflict["course1"])
        courses_involved.add(conflict["course2"])

        # Sort courses for consistent ordering
        course1, course2 = sorted([conflict["course1"], conflict["course2"]])
        pair = (course1, course2)

        # Store in appropriate conflict dict with date and time
        if "Mid" in (conflict["type1"], conflict["type2"]):
            mid_conflicts[pair] = {
                "date": conflict["date"],
                "time": conflict["time1"],
            }
        if "Final" in (conflict["type1"], conflict["type2"]):
            final_conflicts[pair] = {
                "date": conflict["date"],
                "time": conflict["time1"],
            }

    if not mid_conflicts and not final_conflicts:
        return ""

    # Build message with proper formatting
    message = "Exam Conflicts\n\n"
    message += f"Affected Courses: {', '.join(sorted(courses_involved))}\n\n"

    # Add midterm conflicts if any exist
    if mid_conflicts:
        message += "Midterm Conflicts\n"
        for (course1, course2), details in sorted(mid_conflicts.items()):
            message += f"{course1} ↔ {course2}: {details['date']}, {details['time']}\n"

    # Add final conflicts if any exist
    if final_conflicts:
        if mid_conflicts:  # Add extra line break if we had midterm conflicts
            message += "\n"
        message += "Final Conflicts\n"
        for (course1, course2), details in sorted(final_conflicts.items()):
            message += f"{course1} ↔ {course2}: {details['date']}, {details['time']}\n"

    return message.strip()


def check_and_return_exam_conflicts(sections):
    """Check for exam conflicts among the given sections and return formatted message if conflicts exist."""
    exam_conflicts = []
    for i in range(len(sections)):
        section1 = sections[i]
        for j in range(i + 1, len(sections)):
            section2 = sections[j]
            conflicts = check_exam_conflicts(section1, section2)
            exam_conflicts.extend(conflicts)

    if exam_conflicts:
        error_message = format_exam_conflicts_message(exam_conflicts)
        return jsonify({"error": error_message}), 200
    return None


def get_required_days_for_course(sections):
    """Get all required days for a course's sections."""
    required_days = set()
    for section in sections:
        # Check class schedules
        if section.get("sectionSchedule") and section["sectionSchedule"].get(
            "classSchedules"
        ):
            for schedule in section["sectionSchedule"]["classSchedules"]:
                if schedule.get("day"):
                    required_days.add(schedule["day"].upper())

        # Check lab schedules
        for lab in get_lab_schedules_flat(section):
            if lab.get("day"):
                required_days.add(lab["day"].upper())

    return required_days


def check_exam_compatibility(sections):
    """Check if a set of sections has any exam conflicts. Returns (has_conflicts, error_message)."""
    exam_conflicts = []
    
    # Check all possible pairs of sections, but skip different sections of the same course
    for i, section1 in enumerate(sections):
        for j in range(i + 1, len(sections)):
            section2 = sections[j]
            
            # Skip conflict checking between different sections of the same course
            # since they can have different exam schedules
            course1 = section1.get('courseCode', '')
            course2 = section2.get('courseCode', '')
            if course1 == course2:
                continue
                
            conflicts = check_exam_conflicts(section1, section2)
            if conflicts:
                exam_conflicts.extend(conflicts)

    if exam_conflicts:
        error_message = format_exam_conflicts_message(exam_conflicts)
        return True, error_message

    return False, None


def normalize_time(time_str):
    """Normalize time string to HH:MM:SS format."""
    if not time_str:
        debugprint("Warning: Empty time string")
        return "00:00:00"

    time_str = time_str.strip().upper()
    debugprint(f"Normalizing time: {time_str}")

    try:
        # Handle AM/PM format
        if "AM" in time_str or "PM" in time_str:
            # Remove any seconds if present
            time_str = re.sub(r":\d+\s*(AM|PM)", r" \1", time_str)
            # Add missing colons if needed (e.g., "8 AM" -> "8:00 AM")
            if ":" not in time_str:
                time_str = time_str.replace(" ", ":00 ")
            try:
                dt = datetime.strptime(time_str, "%I:%M %p")
                result = dt.strftime("%H:%M:%S")
                debugprint(f"Normalized {time_str} to {result} (12-hour format)")
                return result
            except ValueError:
                try:
                    dt = datetime.strptime(time_str, "%I:%M:%S %p")
                    result = dt.strftime("%H:%M:%S")
                    debugprint(f"Normalized {time_str} to {result} (12-hour format with seconds)")
                    return result
                except ValueError:
                    # Try one more time with flexible parsing
                    time_str = re.sub(
                        r"(\d{1,2})(?:\s*:\s*(\d{2}))?\s*(AM|PM)", r"\1:\2 \3", time_str
                    )
                    # Fix the string joining operation
                    parts = time_str.replace(":", ":00:").split(":")
                    time_str = ":".join(parts[0:2]) + " " + time_str.split()[-1]
                    dt = datetime.strptime(time_str, "%I:%M %p")
                    result = dt.strftime("%H:%M:%S")
                    debugprint(f"Normalized {time_str} to {result} (12-hour format with flexible parsing)")
                    return result
        else:
            # Handle 24-hour format
            parts = time_str.split(":")
            if len(parts) == 1:  # Just hours
                result = f"{int(parts[0]):02d}:00:00"
                debugprint(f"Normalized {time_str} to {result} (24-hour format, hours only)")
                return result
            elif len(parts) == 2:  # Hours and minutes
                result = f"{int(parts[0]):02d}:{int(parts[1]):02d}:00"
                debugprint(f"Normalized {time_str} to {result} (24-hour format, hours and minutes)")
                return result
            else:  # Full time
                result = f"{int(parts[0]):02d}:{int(parts[1]):02d}:{int(parts[2]):02d}"
                debugprint(f"Normalized {time_str} to {result} (24-hour format, full time)")
                return result
    except Exception as e:
        debugprint(f"Error normalizing time {time_str}: {e}")
        return "00:00:00"  # Return midnight if parsing fails


def filter_section_by_time(section, selected_times):
    """Check if section schedules fit within selected time ranges."""
    debugprint(f"\nFiltering section {section.get('courseCode')} {section.get('sectionName')} by time")
    if not selected_times:  # If no times selected, accept all
        debugprint("No time restrictions, accepting section")
        return True, "No time restrictions"

    def time_in_ranges(schedule_type, day, start_time, end_time):
        try:
            if not start_time or not end_time:
                debugprint(f"Missing time data for {schedule_type}, accepting schedule")
                return True, None  # Accept if missing time data

            # Normalize times
            start_time = normalize_time(start_time)
            end_time = normalize_time(end_time)
            debugprint(f"Checking {schedule_type} schedule: {day} {start_time}-{end_time}")

            start_minutes = TimeUtils.time_to_minutes(start_time)
            end_minutes = TimeUtils.time_to_minutes(end_time)

            # Use selected times as-is (they should match TIME_SLOTS format)
            normalized_selected_times = selected_times

            # For lab sessions, we need to ensure ALL required time slots are
            # selected
            if schedule_type == "Lab":
                debugprint("Processing lab schedule")
                # Validate lab duration (allow any reasonable duration)
                lab_duration = end_minutes - start_minutes
                if lab_duration < 60:  # Allow labs as short as 1 hour
                    debugprint(f"Lab duration ({lab_duration} minutes) is too short")
                    return (
                        False,
                        f"Lab session duration ({lab_duration} minutes) is too short",
                    )

                # Get all time slots that this lab session spans
                required_slots = []
                for time_slot in TIME_SLOTS:
                    slot_start, slot_end = time_slot.split("-")
                    # Parse 12-hour format directly without normalizing
                    start_dt = datetime.strptime(slot_start.strip(), "%I:%M %p")
                    end_dt = datetime.strptime(slot_end.strip(), "%I:%M %p")
                    range_start = start_dt.hour * 60 + start_dt.minute
                    range_end = end_dt.hour * 60 + end_dt.minute

                    # If this slot overlaps with the lab session, it's required
                    if start_minutes <= range_end and end_minutes >= range_start:
                        required_slots.append(time_slot)
                        debugprint(f"Found required time slot: {time_slot}")

                # Check if all required slots are selected
                if not all(slot in normalized_selected_times for slot in required_slots):
                    missing_slots = [slot for slot in required_slots if slot not in normalized_selected_times]
                    debugprint(f"Missing required time slots: {', '.join(missing_slots)}")
                    return (
                        False,
                        f"Lab session requires all time slots it spans to be selected: {', '.join(required_slots)}",
                    )
                debugprint("All required time slots are selected")
                return True, None

            # For regular classes, check if the schedule overlaps with selected time slots
            debugprint("Processing regular class schedule")
            schedule_fits = False
            
            # Map TIME_SLOTS to minutes for comparison
            time_slot_ranges = {}
            for time_slot in TIME_SLOTS:
                slot_start, slot_end = time_slot.split("-")
                # Parse 12-hour format directly without normalizing
                start_dt = datetime.strptime(slot_start.strip(), "%I:%M %p")
                end_dt = datetime.strptime(slot_end.strip(), "%I:%M %p")
                range_start = start_dt.hour * 60 + start_dt.minute
                range_end = end_dt.hour * 60 + end_dt.minute
                time_slot_ranges[time_slot] = {
                    'start': range_start,
                    'end': range_end
                }

            # Check which time slots are selected
            debugprint(f"Selected times: {normalized_selected_times}")
            debugprint(f"Available time slots: {list(time_slot_ranges.keys())}")
            
            # Check if schedule overlaps with any selected time slot
            for time_slot in normalized_selected_times:
                if time_slot in time_slot_ranges:
                    range_start = time_slot_ranges[time_slot]['start']
                    range_end = time_slot_ranges[time_slot]['end']
                    
                    debugprint(f"Checking overlap with time slot {time_slot} ({range_start}-{range_end})")
                    
                    # Check if the schedule overlaps with this time slot
                    if start_minutes < range_end and end_minutes > range_start:
                        debugprint(f"Schedule overlaps with selected time slot {time_slot}")
                        schedule_fits = True
                        break

            if not schedule_fits:
                debugprint(f"Schedule {start_time}-{end_time} doesn't overlap with any selected time slot")
                return (
                    False,
                    f"{schedule_type} time {start_time}-{end_time} doesn't overlap with any selected time slot",
                )
            
            debugprint("Schedule fits within selected time slot")
            return True, None

        except Exception as e:
            debugprint(f"Error in time_in_ranges: {e}")
            return True, None  # Accept the section if there's an error in time parsing

    # Check class schedules
    debugprint("Checking class schedules")
    if section.get("sectionSchedule") and section["sectionSchedule"].get(
        "classSchedules"
    ):
        for schedule in section["sectionSchedule"]["classSchedules"]:
            valid, error = time_in_ranges(
                "Class",
                schedule.get("day", ""),
                schedule.get("startTime", ""),
                schedule.get("endTime", ""),
            )
            if not valid:
                debugprint(f"Class schedule invalid: {error}")
                return False, error

    # Check lab schedules
    debugprint("Checking lab schedules")
    for lab in get_lab_schedules_flat(section):
        valid, error = time_in_ranges(
            "Lab",
            lab.get("day", ""),
            lab.get("startTime", ""),
            lab.get("endTime", ""),
        )
        if not valid:
            debugprint(f"Lab schedule invalid: {error}")
            return False, error

    debugprint("All schedules fit within selected times")
    return True, None


def check_schedule_compatibility(schedule1, schedule2):
    """Check if two schedules are compatible (no time conflicts)."""
    try:
        debugprint("\n=== STEP 2: Checking Time Conflicts ===")
        
        # Safely get day values with .get()
        day1 = schedule1.get("day", "").upper() if isinstance(schedule1, dict) else ""
        day2 = schedule2.get("day", "").upper() if isinstance(schedule2, dict) else ""
        
        debugprint(f"Checking schedule compatibility:")
        debugprint(f"Schedule 1: Day={day1}, Start={schedule1.get('startTime', '')}, End={schedule1.get('endTime', '')}")
        debugprint(f"Schedule 2: Day={day2}, Start={schedule2.get('startTime', '')}, End={schedule2.get('endTime', '')}")
        
        if day1 != day2:
            debugprint(f"Different days ({day1} vs {day2}), no conflict")
            return True

        # Safely get time values with .get()
        start1 = TimeUtils.time_to_minutes(normalize_time(schedule1.get("startTime", "")))
        end1 = TimeUtils.time_to_minutes(normalize_time(schedule1.get("endTime", "")))
        start2 = TimeUtils.time_to_minutes(normalize_time(schedule2.get("startTime", "")))
        end2 = TimeUtils.time_to_minutes(normalize_time(schedule2.get("endTime", "")))

        compatible = not schedules_overlap(start1, end1, start2, end2)
        debugprint(f"Schedules are {'compatible' if compatible else 'not compatible'}")
        return compatible
    except Exception as e:
        debugprint(f"Error in check_schedule_compatibility: {e}")
        return False  # If there's any error, assume there's a conflict to be safe


def get_all_schedules(section):
    """Get all schedules (both class and lab) for a section."""
    debugprint(f"\nGetting all schedules for section {section.get('courseCode')} {section.get('sectionName')}")
    schedules = []
    # Add class schedules
    if section.get("sectionSchedule") and section["sectionSchedule"].get(
        "classSchedules"
    ):
        class_schedules = section["sectionSchedule"]["classSchedules"]
        schedules.extend(class_schedules)
        debugprint(f"Added {len(class_schedules)} class schedules")
        for sched in class_schedules:
            debugprint(f"Class schedule: {sched.get('day')} {sched.get('startTime')}-{sched.get('endTime')}")
    
    # Add lab schedules using the flat helper function
    lab_schedules = get_lab_schedules_flat(section)
    schedules.extend(lab_schedules)
    debugprint(f"Added {len(lab_schedules)} lab schedules")
    for lab in lab_schedules:
        debugprint(f"Lab schedule: {lab.get('day')} {lab.get('startTime')}-{lab.get('endTime')}")
    
    debugprint(f"Total schedules: {len(schedules)}")
    return schedules


def is_valid_combination(sections):
    """Check if a combination of sections has any schedule conflicts using optimized algorithm."""
    debugprint("\nChecking if section combination is valid")
    
    if len(sections) <= 1:
        return True
    
    # Pre-process all sections and their schedules with optimization
    section_data = []
    
    # Use sets for O(1) lookups
    seen_courses = set()
    seen_faculty = set()
    
    for section in sections:
        schedules = get_all_schedules(section)
        if schedules:
            course_code = section.get('courseCode')
            faculties = section.get('faculties')
            
            # O(1) duplicate detection
            course_key = f"{course_code}|{faculties}"
            if course_key in seen_courses:
                debugprint(f"Skipping schedule compatibility check between sections of the same course and faculty: {course_code} ({faculties})")
                continue
            seen_courses.add(course_key)
            
            # Pre-group schedules by day for O(1) lookups
            day_schedules = {}
            for sched in schedules:
                day = sched.get('day', '').upper()
                if day:
                    if day not in day_schedules:
                        day_schedules[day] = []
                    # Convert times once and store for reuse
                    start_time = TimeUtils.time_to_minutes(sched.get('startTime', ''))
                    end_time = TimeUtils.time_to_minutes(sched.get('endTime', ''))
                    day_schedules[day].append((start_time, end_time, sched))
            
            section_data.append({
                'section': section,
                'day_schedules': day_schedules,
                'course_code': course_code,
                'faculties': faculties
            })
    
    # Check for internal conflicts in each section - optimized
    debugprint("Checking for internal conflicts")
    for data in section_data:
        day_schedules = data['day_schedules']
        
        # Check conflicts within each day using sorted intervals
        for day, day_scheds in day_schedules.items():
            if len(day_scheds) > 1:
                # Sort by start time for efficient overlap detection
                day_scheds.sort(key=lambda x: x[0])
                
                # Single pass overlap detection
                prev_end = day_scheds[0][1]
                for start, end, _ in day_scheds[1:]:
                    if start < prev_end:
                        debugprint(f"Found internal conflict in {data['course_code']} section")
                        return False
                    prev_end = max(prev_end, end)
    
    # Check conflicts between different sections - optimized
    debugprint("Checking conflicts with other sections")
    
    # Use day-based conflict detection
    for i, data1 in enumerate(section_data):
        day_schedules1 = data1['day_schedules']
        course_code1 = data1['course_code']
        
        for j in range(i + 1, len(section_data)):
            data2 = section_data[j]
            day_schedules2 = data2['day_schedules']
            course_code2 = data2['course_code']
            
            # Find common days efficiently
            common_days = set(day_schedules1.keys()) & set(day_schedules2.keys())
            
            # Check conflicts on common days only
            for day in common_days:
                scheds1 = day_schedules1[day]
                scheds2 = day_schedules2[day]
                
                # Optimize by sorting both lists and using two-pointer technique
                scheds1.sort(key=lambda x: x[0])
                scheds2.sort(key=lambda x: x[0])
                
                # Efficient overlap detection between two sorted lists
                ptr1 = ptr2 = 0
                while ptr1 < len(scheds1) and ptr2 < len(scheds2):
                    start1, end1, _ = scheds1[ptr1]
                    start2, end2, _ = scheds2[ptr2]
                    
                    # Check for overlap
                    if start1 < end2 and start2 < end1:
                        debugprint(f"Found conflict between {course_code1} and {course_code2}")
                        return False
                    
                    # Move pointer with smaller end time
                    if end1 <= end2:
                        ptr1 += 1
                    else:
                        ptr2 += 1
    
    debugprint("No conflicts found, combination is valid")
    return True


def try_all_section_combinations(course_sections_map, selected_days, selected_times):
    """Try all possible combinations of sections to find a valid routine."""
    try:
        debugprint("\n=== Trying Section Combinations ===")
        
        # Get all possible combinations
        courses = list(course_sections_map.keys())
        all_combinations = list(itertools.product(*[course_sections_map[course] for course in courses]))
        print(f"Generated {len(all_combinations)} possible combinations")
        
        # Convert selected times to minutes for easier comparison
        time_ranges = []
        for time_slot in selected_times:
            start, end = time_slot.split("-")
            start_mins = TimeUtils.time_to_minutes(start.strip())
            end_mins = TimeUtils.time_to_minutes(end.strip())
            time_ranges.append((start_mins, end_mins))
            
        print(f"\nSelected time ranges:")
        for start, end in time_ranges:
            print(f"• {TimeUtils.minutes_to_time(start)} - {TimeUtils.minutes_to_time(end)}")
            
        # Iterate through combinations
        print("\nChecking combinations for conflicts...")
        valid_combinations = []
        
        # Pre-compute selected days and time ranges for O(1) lookups
        selected_days_set = set(selected_days)
        time_ranges_tuples = [(start, end) for start, end in time_ranges]
        
        for idx, combination in enumerate(all_combinations, 1):
            print(f"\nTrying combination {idx}/{len(all_combinations)}")
            
            # Check if all sections are within selected days and times
            valid = True
            conflicts = []
            
            # Use set for O(1) course code lookups
            seen_courses = set()
            
            # Check for time conflicts using optimized algorithm
            # Build schedule map for O(1) conflict detection
            schedule_map = {}
            
            for section in combination:
                course_code = section.get("courseCode")
                
                # O(1) course duplicate check
                if course_code in seen_courses:
                    valid = False
                    conflicts.append(f"Cannot take multiple sections of {course_code}")
                    break
                seen_courses.add(course_code)
                
                # Collect all schedules for this section
                section_schedules = []
                
                # Process class schedules
                if section.get("sectionSchedule"):
                    for schedule in section["sectionSchedule"].get("classSchedules", []):
                        day = schedule.get("day", "").upper()
                        if day not in selected_days_set:
                            valid = False
                            conflicts.append(f"{course_code} requires {day}")
                            break
                            
                        start_time = TimeUtils.time_to_minutes(schedule.get("startTime", ""))
                        end_time = TimeUtils.time_to_minutes(schedule.get("endTime", ""))
                        
                        # O(1) time range check
                        time_valid = any(
                            start_time >= time_start and end_time <= time_end
                            for time_start, time_end in time_ranges_tuples
                        )
                        
                        if not time_valid:
                            valid = False
                            conflicts.append(f"{course_code} time conflict")
                            break
                            
                        # Add to schedule map for conflict detection
                        if day not in schedule_map:
                            schedule_map[day] = []
                        schedule_map[day].append((start_time, end_time, course_code))
                
                if not valid:
                    break
                
                # Process lab schedules
                lab_schedules = get_lab_schedules_flat(section)
                for lab in lab_schedules:
                    day = lab.get("day", "").upper()
                    if day not in selected_days_set:
                        valid = False
                        conflicts.append(f"{course_code} Lab requires {day}")
                        break
                        
                    start_time = TimeUtils.time_to_minutes(lab.get("startTime", ""))
                    end_time = TimeUtils.time_to_minutes(lab.get("endTime", ""))
                    
                    time_valid = any(
                        start_time >= time_start and end_time <= time_end
                        for time_start, time_end in time_ranges_tuples
                    )
                    
                    if not time_valid:
                        valid = False
                        conflicts.append(f"{course_code} Lab time conflict")
                        break
                        
                    # Add to schedule map for conflict detection
                    if day not in schedule_map:
                        schedule_map[day] = []
                    schedule_map[day].append((start_time, end_time, course_code))
                
                if not valid:
                    break
                
                # O(n) conflict detection using sorted intervals
                for day, schedules in schedule_map.items():
                    if len(schedules) > 1:
                        # Sort schedules by start time for efficient conflict detection
                        schedules.sort(key=lambda x: x[0])
                        prev_end = schedules[0][1]
                        for start, end, course in schedules[1:]:
                            if start < prev_end:
                                valid = False
                                conflicts.append(f"Time conflict on {day}")
                                break
                            prev_end = end
                        if not valid:
                            break
                
                if not valid:
                    break
            
            if not valid:
                print("\nConflicts found:")
                for conflict in conflicts:
                    print(f"• {conflict}")
                continue
            
            # Check if sections fit within selected days and times
            for section in combination:
                course_code = section.get("courseCode")
                section_name = section.get("sectionName")
                print(f"\nChecking {course_code} Section {section_name}")
                
                # Check class schedules
                if section.get("sectionSchedule"):
                    for schedule in section["sectionSchedule"].get("classSchedules", []):
                        day = schedule.get("day", "").upper()
                        if day not in selected_days:
                            print(f"❌ Class day {day} not in selected days")
                            valid = False
                            conflicts.append(f"{course_code} requires {day}")
                            break
                            
                        start_time = TimeUtils.time_to_minutes(schedule.get("startTime", ""))
                        end_time = TimeUtils.time_to_minutes(schedule.get("endTime", ""))
                        
                        # Check if class time is within any selected time slot
                        time_valid = False
                        for time_start, time_end in time_ranges:
                            if start_time >= time_start and end_time <= time_end:
                                time_valid = True
                                break
                                
                        if not time_valid:
                            print(f"❌ Class time {schedule.get('startTime')} - {schedule.get('endTime')} outside selected times")
                            valid = False
                            conflicts.append(f"{course_code} time conflict")
                            break
                            
                # Check lab schedules
                lab_schedules = get_lab_schedules_flat(section)
                for lab in lab_schedules:
                    day = lab.get("day", "").upper()
                    if day not in selected_days:
                        print(f"❌ Lab day {day} not in selected days")
                        valid = False
                        conflicts.append(f"{course_code} Lab requires {day}")
                        break
                        
                    start_time = TimeUtils.time_to_minutes(lab.get("startTime", ""))
                    end_time = TimeUtils.time_to_minutes(lab.get("endTime", ""))
                    
                    # Check if lab time is within any selected time slot
                    time_valid = False
                    for time_start, time_end in time_ranges:
                        if start_time >= time_start and end_time <= time_end:
                            time_valid = True
                            break
                            
                    if not time_valid:
                        print(f"❌ Lab time {lab.get('startTime')} - {lab.get('endTime')} outside selected times")
                        valid = False
                        conflicts.append(f"{course_code} Lab time conflict")
                        break
                        
                if not valid:
                    break
            
            if valid:
                print("\n✅ Found valid combination!")
                valid_combinations.append(list(combination))
                
            if not valid:
                print("\nConflicts in combination {idx}:")
                for conflict in conflicts:
                    print(f"• {conflict}")
        
        if valid_combinations:
            # Return the first valid combination
            return valid_combinations[0], None
                
        print("\n❌ No valid combination found")
        return None, "Could not find a valid combination without conflicts. Please try different sections or time slots."
        
    except Exception as e:
        print(f"\n❌ Error finding combinations: {e}")
        traceback.print_exc()
        return None, f"Error finding valid combinations: {e}"


@app.route("/api/routine", methods=["POST"])
def generate_routine():
    try:
        # Load fresh data for each routine generation request
        debugprint("\n=== Loading Fresh Course Data ===")
        fresh_data = load_data()  # Get fresh data from the API
        if not fresh_data:
            return jsonify({
                "error": True,
                "title": "Data Loading Error",
                "message": "We couldn't load the current course data from the server.",
                "suggestion": "Please try again later or contact support if the issue persists."
            }), 503
        
        # Get request data
        request_data = request.get_json()
        debugprint("\n=== Request Data ===")
        debugprint("Raw request data:", request_data)
        
        if not request_data:
            return jsonify({
                "error": True,
                "title": "Missing Request Data",
                "message": "No data was provided in your request.",
                "suggestion": "Please ensure you're submitting course selections and preferences."
            }), 400

        # Handle both old and new request formats
        days = request_data.get("days", [])
        times = request_data.get("times", [])
        use_ai = request_data.get("useAI", False)
        commute_preference = request_data.get("commutePreference", "")
        
        if "courses" in request_data:
            courses = request_data["courses"]
            # Handle the case where courses is a list of objects with course and sections properties
            if courses and isinstance(courses, list) and isinstance(courses[0], dict) and "course" in courses[0]:
                debugprint("Detected course objects format")
                # This is already in the expected format
                pass
            # Handle the case where courses is a list of course codes
            elif courses and isinstance(courses, list) and isinstance(courses[0], str):
                debugprint("Detected course codes format, converting to course objects")
                # Convert to course objects format
                courses = [{"course": course, "sections": {}} for course in courses]
                debugprint(f"Converted course codes to course objects: {courses}")
            else:
                return jsonify({
                    "error": True,
                    "title": "Invalid Format",
                    "message": "The courses data format in your request is invalid.",
                    "suggestion": "Please ensure you're using the correct format for course selections."
                }), 400
        elif "sections" in request_data:
            # Handle direct section IDs from regular routine generation
            section_ids = request_data["sections"]
            debugprint(f"\n=== Processing Direct Section IDs: {section_ids} ===")
            
            # Find all sections in fresh data
            all_sections = []
            for section_id in section_ids:
                matching_section = next((s for s in fresh_data if s.get("section") == section_id), None)
                # If not found by section ID, try matching by sectionName
                if not matching_section:
                    matching_section = next((s for s in fresh_data if s.get("sectionName") == section_id), None)
                if matching_section:
                    all_sections.append(matching_section)
                    debugprint(f"Found section: {matching_section.get('courseCode')} - {matching_section.get('sectionName')}")
                else:
                    debugprint(f"Section not found: {section_id}")
            
            if not all_sections:
                return jsonify({"error": "No valid sections found"}), 400
                
            # Group sections by course code
            courses_map = {}
            for section in all_sections:
                course_code = section.get("courseCode")
                if course_code not in courses_map:
                    courses_map[course_code] = []
                courses_map[course_code].append(section)
                
            # Format courses for processing
            courses = []
            for course_code, sections in courses_map.items():
                courses.append({
                    "course": course_code,
                    "sections": {section.get("faculties"): {"value": section.get("sectionName")} for section in sections},
                    "locked": True  # Mark as locked since sections were provided directly
                })
            
            debugprint(f"Formatted courses from sections: {courses}")
        else:
            return jsonify({
                "error": True,
                "title": "Missing Course Information",
                "message": "No courses or sections were provided in your request.",
                "suggestion": "Please select at least one course or section to generate a routine."
            }), 400
            
        # Get all possible combinations
        all_combinations = []
        
        # Check if we need to optimize faculty selection for minimum days
        optimize_faculty = (commute_preference == "far" and 
                           all(len(course.get("sections", {})) == 0 for course in courses))
        
        if optimize_faculty:
            debugprint("=== Optimizing faculty selection for minimum campus days ===")
            
            # Build faculty options for each course
            course_faculty_options = {}
            for course in courses:
                course_code = course["course"]
                available_sections = [s for s in fresh_data if s.get("courseCode") == course_code]
                
                # Group sections by faculty
                faculty_sections = {}
                for section in available_sections:
                    # Skip seat availability check for explicitly provided sections or locked courses
                    if course.get("locked", False) or section.get("capacity", 0) - section.get("consumedSeat", 0) > 0:
                        faculty = section.get("faculties", "TBA") or "TBA"
                        if faculty not in faculty_sections:
                            faculty_sections[faculty] = []
                        faculty_sections[faculty].append(section)
                
                course_faculty_options[course_code] = faculty_sections
                debugprint(f"{course_code}: {len(faculty_sections)} faculty options")
            
            # Use a more efficient approach - evaluate faculty combinations lazily
            course_codes = [course["course"] for course in courses]
            
            # Generate all faculty combinations
            from itertools import product
            faculty_lists = [list(course_faculty_options[code].keys()) for code in course_codes]
            total_combinations = 1
            for fl in faculty_lists:
                total_combinations *= len(fl)
            
            debugprint(f"Evaluating {total_combinations} faculty combinations...")
            
            best_combination = None
            min_days = float('inf')
            
            # Evaluate faculty combinations in batches to avoid memory issues
            evaluated = 0
            for faculty_combo in product(*faculty_lists):
                evaluated += 1
                if evaluated % 100 == 0:
                    debugprint(f"Evaluated {evaluated}/{total_combinations} combinations...")
                
                # Build sections for this faculty combination
                temp_sections = []
                for i, course_code in enumerate(course_codes):
                    faculty = faculty_combo[i]
                    sections = course_faculty_options[course_code][faculty]
                    temp_sections.append(sections)
                
                # Calculate campus days for this combination
                try:
                    # Quick evaluation using first available combination
                    test_combination = next(itertools.product(*temp_sections))
                    unique_days = set()
                    
                    for section in test_combination:
                        # Add class days
                        if section.get("sectionSchedule") and section["sectionSchedule"].get("classSchedules"):
                            for schedule in section["sectionSchedule"]["classSchedules"]:
                                unique_days.add(schedule["day"].upper())
                        
                        # Add lab days
                        for lab in get_lab_schedules_flat(section):
                            unique_days.add(lab["day"].upper())
                    
                    days_count = len(unique_days)
                    
                    if days_count < min_days:
                        min_days = days_count
                        best_combination = temp_sections
                        debugprint(f"New best: {faculty_combo} = {days_count} days")
                        
                        # Early exit if we found the absolute minimum
                        if days_count <= 1:
                            break
                            
                except StopIteration:
                    continue
            
            debugprint(f"Evaluation complete. Best combination: {min_days} days")
            
            if best_combination:
                all_combinations = best_combination
            else:
                # Fallback to original behavior
                for course in courses:
                    course_code = course["course"]
                    available_sections = [s for s in fresh_data if s.get("courseCode") == course_code]
                    
                    # Check if course is locked (sections provided directly)
                    is_locked_course = course.get("locked", False)
                    sections_by_faculty = course.get("sections", {})
                    course_sections = []
                    for section in available_sections:
                        is_locked_section = any(
                            section.get("sectionName") == info.get("value") 
                            for info in sections_by_faculty.values()
                        )
                        if is_locked_course or is_locked_section or section.get("capacity", 0) - section.get("consumedSeat", 0) > 0:
                            course_sections.append(section)
                    
                    all_combinations.append(course_sections)
        else:
            # Enhanced logic for when specific faculties are selected - evaluate all combinations globally
            for course in courses:
                course_code = course["course"]
                sections_by_faculty = course.get("sections", {})
                
                debugprint(f"\n=== Processing Course: {course_code} ===")
                
                # Find all sections for the course
                available_sections = [s for s in fresh_data if s.get("courseCode") == course_code]
                
                if not available_sections:
                    debugprint(f"❌ Course not found in fresh data: {course_code}")
                    return jsonify({
                        "error": True,
                        "title": "Course Not Found",
                        "message": f"We couldn't find {course_code} in the current course offerings. Please check the course code and try again.",
                        "suggestion": "Try searching for a different course or check if the semester offerings have changed."
                    }), 400

                # Global faculty optimization: evaluate all faculty combinations across all courses
                if sections_by_faculty and any(faculty for faculty in sections_by_faculty.keys()):
                    debugprint("\n=== Global Faculty Optimization: Finding Minimum Days Across All Courses ===")
                    
                    # Build faculty-to-sections mapping for this course
                    faculty_sections = {}
                    for section in available_sections:
                        # Check if this section is explicitly locked or course is locked
                        is_locked = any(
                            section.get("sectionName") == info.get("value") 
                            for info in sections_by_faculty.values()
                        )
                        
                        if is_locked or course.get("locked", False) or section.get("capacity", 0) - section.get("consumedSeat", 0) > 0:
                            faculty_name = section.get("faculties", "TBA")
                            if faculty_name.upper() == "TBA" or not faculty_name.strip():
                                faculty_name = "TBA"
                            
                            # Check if this faculty was requested
                            if faculty_name in sections_by_faculty or "TBA" in sections_by_faculty:
                                if faculty_name not in faculty_sections:
                                    faculty_sections[faculty_name] = []
                                faculty_sections[faculty_name].append(section)
                    
                    # Instead of optimizing per course, collect all sections from all requested faculties
                    # Check if we have explicitly provided sections to use instead of fresh data
                    sections_by_faculty = course.get("sections", {})
                    has_provided_sections = any(section_info.get("section") for section_info in sections_by_faculty.values())
                    
                    if has_provided_sections:
                        # Use provided section data directly, ignoring fresh data
                        debugprint(f"=== Using provided section data for {course_code} ===")
                        course_sections = []
                        for faculty, section_info in sections_by_faculty.items():
                            section_data = section_info.get("section")
                            if section_data:
                                # Use the exact provided section regardless of seat availability
                                course_sections.append(section_data)
                                debugprint(f"Added provided section: {section_data.get('sectionName')} with faculty {faculty}")
                        all_combinations.append(course_sections)
                    elif faculty_sections:
                        # Collect all sections from all requested faculties for this course (fresh data)
                        course_sections = []
                        for faculty, sections in faculty_sections.items():
                            course_sections.extend(sections)
                        
                        debugprint(f"Collected {len(course_sections)} sections from {len(faculty_sections)} faculties for {course_code}")
                        all_combinations.append(course_sections)
                    else:
                        # Fallback to fresh data with seat availability check
                        course_sections = []
                        for faculty, section_info in sections_by_faculty.items():
                            section_name = section_info.get("value")
                            if section_name:
                                if faculty.upper() == "TBA":
                                    matching_sections = [
                                        s for s in available_sections 
                                        if s.get("sectionName") == section_name 
                                        and (not s.get("faculties") or s.get("faculties").strip() == "" or s.get("faculties").upper() == "TBA")
                                    ]
                                else:
                                    matching_sections = [
                                        s for s in available_sections 
                                        if s.get("sectionName") == section_name 
                                        and s.get("faculties") == faculty
                                    ]
                                course_sections.extend(matching_sections)
                            else:
                                if faculty.upper() == "TBA":
                                    faculty_sections = [
                                        s for s in available_sections 
                                        if (not s.get("faculties") or s.get("faculties").strip() == "" or s.get("faculties").upper() == "TBA")
                                    ]
                                else:
                                    faculty_sections = [
                                        s for s in available_sections 
                                        if s.get("faculties") == faculty
                                    ]
                                course_sections.extend(faculty_sections)
                        all_combinations.append(course_sections)
                else:
                    # Check if we have explicitly provided sections to use instead of fresh data
                    sections_by_faculty = course.get("sections", {})
                    has_provided_sections = any(section_info.get("section") for section_info in sections_by_faculty.values())
                    
                    if has_provided_sections:
                        # Use provided section data directly
                        debugprint(f"=== Using provided section data for {course_code} ===")
                        course_sections = []
                        
                        for faculty, section_info in sections_by_faculty.items():
                            section_data = section_info.get("section")
                            if section_data:
                                # Use the exact provided section regardless of seat availability
                                course_sections.append(section_data)
                                debugprint(f"Added provided section: {section_data.get('sectionName')} with faculty {faculty}")
                        
                        all_combinations.append(course_sections)
                    else:
                        # No specific sections provided - use fresh data with availability check
                        is_locked_course = course.get("locked", False)
                        course_sections = []
                        for section in available_sections:
                            is_locked_section = any(
                                section.get("sectionName") == info.get("value") 
                                for info in sections_by_faculty.values()
                            )
                            if is_locked_course or is_locked_section or section.get("capacity", 0) - section.get("consumedSeat", 0) > 0:
                                course_sections.append(section)
                        
                        all_combinations.append(course_sections)
            
            if not course_sections:
                msg = "No available sections found"
                if sections_by_faculty:
                    msg += " matching your selection"
                msg += f" for {course_code}"
                debugprint(f"❌ {msg}")
                return jsonify({
                    "error": True,
                    "title": "No Available Sections",
                    "message": msg,
                    "suggestion": "Try selecting a different faculty or check if the course has available seats in other sections."
                }), 400
            
            debugprint(f"\nFinal sections selected for {course_code}: {len(course_sections)}")
            for section in course_sections:
                debugprint(f"- Section {section.get('sectionName')} with faculty {section.get('faculties')}")
            all_combinations.append(course_sections)

        # Check if we have any valid combinations after processing all courses
        if not all_combinations:
            return jsonify({
                "error": True,
                "title": "No Valid Sections",
                "message": "We couldn't find any valid sections for your selected courses.",
                "suggestion": "Try selecting different courses or check if the courses have available seats."
            }), 400

        # Generate all possible combinations with lazy evaluation
        try:
            # Filter out courses with no valid sections before generating combinations
            valid_course_combinations = [course_sections for course_sections in all_combinations if course_sections]
            
            if not valid_course_combinations:
                return jsonify({
                    "error": True,
                    "title": "No Valid Sections",
                    "message": "We couldn't find any valid sections for your selected courses.",
                    "suggestion": "Try selecting different courses or check if the courses have available seats."
                }), 400
                
            # Pre-filter sections based on day/time preferences to reduce combination space
            prefiltered_combinations = []
            for course_sections in valid_course_combinations:
                filtered_sections = []
                for section in course_sections:
                    # Quick pre-filter based on days if provided
                    if days and days != ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]:
                        section_days = set()
                        if section.get("sectionSchedule") and section["sectionSchedule"].get("classSchedules"):
                            section_days.update(schedule["day"].upper() 
                                for schedule in section["sectionSchedule"]["classSchedules"])
                        for lab in get_lab_schedules_flat(section):
                            section_days.add(lab["day"].upper())
                        
                        # Skip sections that don't match day preferences
                        if not any(day.upper() in [d.upper() for d in days] for day in section_days):
                            continue
                    
                    filtered_sections.append(section)
                
                # Only keep courses that have sections after filtering
                if filtered_sections:
                    prefiltered_combinations.append(filtered_sections)
                else:
                    prefiltered_combinations.append(course_sections)  # Fallback to original
            
            # Use lazy generator instead of materializing all combinations upfront
            combination_generator = itertools.product(*prefiltered_combinations)
            debugprint(f"Starting lazy evaluation for {len(prefiltered_combinations)} courses")
        except Exception as e:
            debugprint(f"Error generating combinations: {str(e)}")
            return jsonify({
                "error": True,
                "title": "Combination Generation Failed",
                "message": "We couldn't generate valid combinations with your selected courses.",
                "suggestion": "Try selecting fewer courses or different sections to reduce complexity."
            }), 400

        if not all_combinations:
            return jsonify({
                "error": True,
                "title": "No Valid Combinations",
                "message": "We couldn't generate any valid combinations with your selected courses.",
                "suggestion": "Try selecting fewer courses at once, choose different sections, or expand your day/time preferences to increase compatibility."
            }), 400

        # STEP 1: Check exam conflicts with lazy evaluation and caching
        debugprint("\n=== STEP 1: Checking Exam Conflicts ===")
        combinations_without_exam_conflicts = []
        processed_count = 0
        valid_count = 0
        start_time = time.time()
        max_processing_time = 30  # Maximum processing time in seconds
        
        # Cache for exam conflict checks to avoid recomputation
        exam_cache = {}
        
        # Process combinations lazily with batch processing
        batch_size = 100  # Process in smaller batches to avoid memory issues
        for combination in combination_generator:
            # Check time limit
            if time.time() - start_time > max_processing_time:
                debugprint(f"Processing timeout after {max_processing_time} seconds")
                break
                
            processed_count += 1
            
            # Validate combination structure
            if not all(isinstance(section, dict) and "courseCode" in section for section in combination):
                continue

            # Create cache key for this combination
            cache_key = tuple(section.get("sectionId", "") for section in combination)
            
            # Check cache first
            if cache_key in exam_cache:
                has_exam_conflicts, exam_error = exam_cache[cache_key]
            else:
                has_exam_conflicts, exam_error = check_exam_compatibility(combination)
                exam_cache[cache_key] = (has_exam_conflicts, exam_error)
            
            if not has_exam_conflicts:
                combinations_without_exam_conflicts.append(combination)
                valid_count += 1
                
                # Early exit if we have enough valid combinations
                if valid_count >= 1000:  # Limit to prevent memory overflow
                    debugprint(f"Found {valid_count} valid combinations after processing {processed_count}")
                    break
            
            # Progress logging
            if processed_count % batch_size == 0:
                debugprint(f"Processed {processed_count} combinations, found {valid_count} valid so far...")
                
            # Quick validation for extremely large datasets
            if processed_count >= 10000 and valid_count == 0:
                debugprint("Warning: Processed 10,000+ combinations with no valid results, stopping early")
                break

        debugprint(f"Total combinations processed: {processed_count}, valid combinations: {valid_count}, time: {time.time() - start_time:.2f}s")

        if not combinations_without_exam_conflicts:
            # For error reporting, we need to process remaining combinations
            debugprint("No valid combinations found, collecting detailed conflict information...")
            remaining_conflicts = []
            
            # Reset generator and process remaining combinations
            combination_generator = itertools.product(*valid_course_combinations)
            for combination in combination_generator:
                cache_key = tuple(section.get("sectionId", "") for section in combination)
                if cache_key not in exam_cache:
                    has_exam_conflicts, exam_error = check_exam_compatibility(combination)
                    exam_cache[cache_key] = (has_exam_conflicts, exam_error)
                else:
                    has_exam_conflicts, exam_error = exam_cache[cache_key]
                    
                if has_exam_conflicts and exam_error:
                    remaining_conflicts.append(exam_error)
                    if len(remaining_conflicts) >= 10:  # Limit conflict details
                        break
            
            # Return the first detailed conflict message
            if remaining_conflicts:
                return jsonify({
                    "error": True,
                    "title": "Exam Conflicts",
                    "message": remaining_conflicts[0],
                    "suggestion": "Try selecting courses with non-overlapping exam schedules, choose different sections of the same courses, or remove one of the conflicting courses."
                }), 200
            else:
                return jsonify({
                    "error": True,
                    "title": "Exam Conflicts",
                    "message": "Exam Conflicts\n\nAll possible combinations have exam schedule conflicts.\n\nTry selecting courses with non-overlapping exam schedules, choose different sections of the same courses, or remove one of the conflicting courses.",
                    "suggestion": "Try selecting courses with non-overlapping exam schedules, choose different sections of the same courses, or remove one of the conflicting courses."
                }), 200

        # STEP 2: Check time conflicts with streaming processing
        debugprint("\n=== STEP 2: Checking Time Conflicts ===")
        valid_combinations = []
        valid_count = 0
        
        # Cache for time conflict checks
        time_cache = {}
        
        for combination in combinations_without_exam_conflicts:
            # Create cache key
            cache_key = tuple(section.get("sectionId", "") for section in combination)
            
            # Check cache first
            if cache_key in time_cache:
                is_valid = time_cache[cache_key]
            else:
                is_valid = is_valid_combination(combination)
                time_cache[cache_key] = is_valid
                
            if is_valid:
                valid_combinations.append(combination)
                valid_count += 1
                
                # Limit valid combinations to prevent memory issues
                if valid_count >= 1000:
                    debugprint(f"Found {valid_count} valid combinations after time conflict check")
                    break

        if not valid_combinations:
            return jsonify({
                "error": True,
                "title": "Time Conflicts Detected",
                "message": "All possible combinations have class time conflicts.",
                "suggestion": "Some of your selected courses have overlapping class times. Try choosing different sections of the same courses or select courses with complementary schedules."
            }), 200

        # STEP 2.5: Cross-course faculty optimization for minimum days
        debugprint("\n=== STEP 2.5: Cross-Course Faculty Optimization ===")
        
        # When faculty is specified for multiple courses, find optimal combination
        has_faculty_specified = any(
            course.get("sections") and any(faculty for faculty in course["sections"].keys())
            for course in courses
        )
        
        if has_faculty_specified and commute_preference in ["far", "Live Far"]:
            debugprint("Optimizing faculty combinations for minimum campus days...")
            
            # Build faculty options for each course
            course_faculty_map = {}
            for course in courses:
                course_code = course["course"]
                course_faculty_map[course_code] = {}
                
                available_sections = [s for s in fresh_data if s.get("courseCode") == course_code
                                    and s.get("capacity", 0) - s.get("consumedSeat", 0) > 0]
                
                sections_by_faculty = course.get("sections", {})
                for faculty in sections_by_faculty.keys():
                    faculty_name = faculty if faculty.upper() != "TBA" else "TBA"
                    faculty_sections = [
                        s for s in available_sections 
                        if (faculty_name == "TBA" and (not s.get("faculties") or s.get("faculties").strip() == "" or s.get("faculties").upper() == "TBA")) or
                           (faculty_name != "TBA" and s.get("faculties") == faculty_name)
                    ]
                    if faculty_sections:
                        course_faculty_map[course_code][faculty_name] = faculty_sections
            
            # Find optimal faculty combination across all courses
            if all(course_faculty_map.values()):
                best_combination = None
                min_days = float('inf')
                
                # Generate all possible faculty combinations
                faculty_combinations = list(itertools.product(
                    *[list(course_faculty_map[code].items()) for code in course_faculty_map]
                ))
                
                for combo in faculty_combinations:
                    # Build test combination - use all sections for each faculty
                    test_sections = []
                    for _, sections in combo:
                        test_sections.extend(sections)
                    
                    if test_sections:  # Only process non-empty combinations
                        days_count, _ = calculate_campus_days(test_sections)
                        
                        if days_count < min_days:
                            min_days = days_count
                            best_combination = [sections for _, sections in combo]
                
                if best_combination:
                    debugprint(f"Found optimal faculty combination: {min_days} days")
                    # Flatten the best combination for processing
                    all_combinations = []
                    for sections in best_combination:
                        all_combinations.extend(sections)
                    
                    # Remove duplicates based on courseCode and sectionName
                    seen = set()
                    unique_combinations = []
                    for section in all_combinations:
                        key = (section.get("courseCode"), section.get("sectionName"))
                        if key not in seen:
                            seen.add(key)
                            unique_combinations.append(section)
                    
                    all_combinations = unique_combinations
                else:
                    debugprint("No optimal faculty combination found, using original logic")

        # STEP 3: Check day/time preferences with streaming processing
        debugprint("\n=== STEP 3: Checking Day/Time Preferences ===")
        final_combinations = []
        final_count = 0
        
        # Cache for preference checks
        preference_cache = {}
        
        for combination in valid_combinations:
            # Create cache key
            cache_key = tuple(section.get("sectionId", "") for section in combination)
            
            # Check cache first
            if cache_key in preference_cache:
                is_valid = preference_cache[cache_key]
            else:
                is_valid = True
                for section in combination:
                    # Check if section schedules fit within selected times
                    valid_time, error = filter_section_by_time(section, times)
                    if not valid_time:
                        is_valid = False
                        break

                    # Check if section days are in selected days
                    section_days = set()
                    if section.get("sectionSchedule") and section["sectionSchedule"].get("classSchedules"):
                        section_days.update(schedule["day"].upper() 
                            for schedule in section["sectionSchedule"]["classSchedules"])
                    for lab in get_lab_schedules_flat(section):
                        section_days.add(lab["day"].upper())
                    
                    if not all(day.upper() in [d.upper() for d in days] for day in section_days):
                        is_valid = False
                        break
                
                preference_cache[cache_key] = is_valid
                
            if is_valid:
                final_combinations.append(combination)
                final_count += 1
                
                # Limit final combinations
                if final_count >= 1000:
                    debugprint(f"Found {final_count} valid combinations after preference check")
                    break

        if not final_combinations:
            return jsonify({
                "error": True,
                "title": "Preference Mismatch",
                "message": "No combinations match your day and time preferences.",
                "suggestion": "Your day/time preferences are too restrictive. Try selecting more days, expanding your preferred time ranges, or choose courses with more flexible scheduling options."
            }), 200

        # Sort combinations by campus days with streaming processing
        debugprint("\n=== Sorting Combinations Based on Commute Preference ===")
        
        # Process ALL combinations to find the actual minimum/maximum days
        combinations_with_days = []
        
        # Process all valid combinations to ensure we find the optimal ones
        for combination in final_combinations:
            days_count, days_list = calculate_campus_days(combination)
            combinations_with_days.append({
                "combination": combination,
                "campus_days": days_count,
                "days_list": days_list
            })

        # Sort based on commute preference
        debugprint(f"\nApplying commute preference: '{commute_preference}'")
        if commute_preference == "far" or commute_preference == "Live Far":
            combinations_with_days.sort(key=lambda x: x["campus_days"])
            debugprint("\nSorted combinations by ascending campus days (fewer days is better)")
        elif commute_preference == "near" or commute_preference == "Live Near":
            combinations_with_days.sort(key=lambda x: -x["campus_days"])
            debugprint("\nSorted combinations by descending campus days (more days is better)")
        else:
            # Balanced approach
            if combinations_with_days:
                all_campus_days = [combo["campus_days"] for combo in combinations_with_days]
                target_days = (min(all_campus_days) + max(all_campus_days)) // 2
                combinations_with_days.sort(key=lambda x: abs(x["campus_days"] - target_days))
                debugprint(f"\nNo preference: sorted combinations by balanced days (target: {target_days} days)")
                    
        # Use the best combination, but limit to prevent memory issues
        max_results = min(100, len(combinations_with_days))  # Limit final results
        best_combination = combinations_with_days[0]["combination"]
        debugprint(f"Selected best combination with {combinations_with_days[0]['campus_days']} campus days")
        debugprint(f"Total combinations processed: {len(combinations_with_days)}")
        debugprint(f"Top 5 combinations by preference:")
        for i, combo in enumerate(combinations_with_days[:5]):
            debugprint(f"  {i+1}. {combo['campus_days']} days: {sorted(combo['days_list'])}")
        
        # Print detailed info about the selected combination
        debugprint("\n=== DETAILED INFO ABOUT SELECTED COMBINATION ===")
        debugprint(f"Commute Preference: {commute_preference}")
        debugprint(f"Campus Days: {combinations_with_days[0]['campus_days']}")
        debugprint(f"Days List: {', '.join(combinations_with_days[0]['days_list'])}")
        
        # If using AI, pass to AI routine generation
        if use_ai:
            debugprint("\n=== Using AI Routine Generation ===")
            return try_ai_routine_generation(best_combination, days, times, commute_preference)
        
        # Return the best combination based on commute preference
        debugprint("\n=== Using Manual Routine Generation with Commute Preference ===")
        
        # Filter to ensure only one faculty per course
        filtered_combination = []
        course_codes_seen = set()
        
        for section in best_combination:
            course_code = section.get("courseCode")
            if course_code not in course_codes_seen:
                filtered_combination.append(section)
                course_codes_seen.add(course_code)
                debugprint(f"Selected {course_code} section with faculty {section.get('faculties')}")
        
        return jsonify({"routine": filtered_combination}), 200

    except Exception as e:
        debugprint(f"Error in generate_routine: {str(e)}")
        return jsonify({
            "error": True,
            "title": "Routine Generation Error",
            "message": "We encountered an unexpected error while generating your routine.",
            "suggestion": "Please try again with different course selections or contact support if the issue persists.",
            "details": str(e) if app.debug else None
        }), 500

def try_ai_routine_generation(valid_combination, selected_days, selected_times, commute_preference):
    """AI-assisted routine generation using Gemini AI."""
    try:
        debugprint("\n=== Using AI for Best Routine ===")
        
        # Check AI availability first
        ai_available, message = check_ai_availability()
        if not ai_available:
            debugprint(f"AI not available: {message}")
            return jsonify({"routine": valid_combination}), 200

        # Calculate routine score
        score = calculate_routine_score(valid_combination, selected_days, selected_times, commute_preference)
        debugprint(f"Routine score: {score}")

        # Get feedback
        feedback = get_routine_feedback_for_api(valid_combination, commute_preference)
        if feedback:
            debugprint("\nAI Feedback:")
            debugprint(feedback)

        return jsonify({
            "routine": valid_combination,
            "score": score,
            "feedback": feedback
        }), 200

    except Exception as e:
        debugprint(f"Error in AI routine generation: {e}")
        return jsonify({"routine": valid_combination}), 200

def get_routine_feedback_for_api(routine, commute_preference=None):
    """Get AI feedback for a routine."""
    try:
        # Check AI availability first
        ai_available, message = check_ai_availability()
        if not ai_available:
            debugprint(f"AI not available: {message}")
            return "AI feedback not available"

        # Get the days used in the routine
        days_used = get_days_used_in_routine(routine)
        days_str = ", ".join(days_used)
        num_days = len(days_used)
        
        debugprint("\n=== Generating AI Feedback ===")
        debugprint(f"Days used: {days_str} ({num_days} days)")
        debugprint(f"Commute preference: {commute_preference}")
        
        # Build the prompt with commute preference context
        prompt = f"Look at this routine:\n{json.dumps(routine)}\n\n"
        prompt += f"This routine requires being on campus for {num_days} day(s): {days_str}.\n"
        
        if commute_preference:
            prompt += f"The student's commute preference is '{commute_preference}'.\n"
            if commute_preference.lower() == "far":
                prompt += "For 'Live Far', fewer days on campus is better with more classes per day.\n"
                # Add specific feedback guidance for 'Live Far'
                if num_days <= 3:
                    prompt += "This is a good compact schedule with few campus days.\n"
                else:
                    prompt += "This schedule could be more compact with fewer campus days.\n"
            elif commute_preference.lower() == "near":
                prompt += "For 'Live Near', more days on campus is better with fewer classes per day.\n"
                # Add specific feedback guidance for 'Live Near'
                if num_days >= 5:
                    prompt += "This is a good spread-out schedule with many campus days.\n"
                else:
                    prompt += "This schedule could be more spread out across more days.\n"
        else:
            prompt += "No specific commute preference was selected, so a balanced schedule is ideal.\n"
        
        prompt += (
            "First, rate this routine out of 10.\n"
            "Then give me 2-3 quick points about:\n"
            "• Schedule overview\n"
            "• What works well\n"
            "• Areas for improvement\n"
            "Keep it casual and under 10 words per point.\n"
            "Format your response exactly like this:\n"
            "Score: X/10\n"
            "Schedule: [brief overview]\n"
            "Good: [what works well]\n"
            "Needs Work: [areas to improve]"
        )

        debugprint("\nGenerating AI response...")
        response = gemini_model.generate_content(prompt)
        feedback = response.text.strip()
        debugprint("AI Feedback:", feedback)
        return feedback

    except Exception as e:
        debugprint(f"Error getting routine feedback: {e}")
        traceback.print_exc()
        return "Error generating AI feedback"


def auto_fix_json(s):
    # Count open/close braces and brackets
    open_braces = s.count("{")
    close_braces = s.count("}")
    open_brackets = s.count("[")
    close_brackets = s.count("]")
    # Add missing closing braces/brackets
    s += "}" * (open_braces - close_braces)
    s += "]" * (open_brackets - close_brackets)
    return s


def format24(time_str):
    # Converts "8:00 AM" to "08:00:00"
    debugprint(f"Converting to 24-hour format: {time_str}")
    try:
        dt = datetime.strptime(time_str.strip(), "%I:%M %p")
        result = dt.strftime("%H:%M:%S")
        debugprint(f"Converted {time_str} to {result} (24-hour format)")
        return result
    except Exception as e:
        debugprint(f"Error converting to 24-hour format: {e}")
        return time_str


def timeToMinutes(tstr):
    # Accepts "08:00:00" or "8:00 AM"
    if not tstr:
        debugprint(f"Warning: Empty time string")
        return 0

    tstr = tstr.strip()
    debugprint(f"Converting time to minutes: {tstr}")
    try:
        if "AM" in tstr or "PM" in tstr:
            dt = datetime.strptime(tstr, "%I:%M %p")
            minutes = dt.hour * 60 + dt.minute
            debugprint(f"Converted {tstr} to {minutes} minutes (12-hour format)")
            return minutes
        else:
            dt = datetime.strptime(tstr, "%H:%M:%S")
            minutes = dt.hour * 60 + dt.minute
            debugprint(f"Converted {tstr} to {minutes} minutes (24-hour format)")
            return minutes
    except Exception as e:
        debugprint(f"Error converting time to minutes: {e}")
        return 0


@app.route("/api/ask_ai", methods=["POST"])
def ask_ai():
    req = request.json
    question = req.get("question", "")
    routine_context = req.get("routine", None)

    if not question:
        return jsonify({"answer": "Please provide a question."}), 400

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")  # Using flash model for better performance

        # Create a context-aware prompt
        prompt = (
            "You are an AI assistant specifically for the USIS Routine Generator. "
            "Your role is to help students with their course schedules and academic planning. "
            "You should ONLY answer questions related to course scheduling, routine generation, "
            "and academic matters within this application.\n\n"
        )

        # If routine context is provided, add it to the prompt
        if routine_context:
            prompt += (
                "The student has generated the following routine:\n"
                f"{json.dumps(routine_context, indent=2)}\n\n"
                "When answering questions, refer to this routine if relevant.\n\n"
            )

        prompt += (
            "Question: " + question + "\n\n"
            "Instructions:\n"
            "1. Only answer questions related to course scheduling and academic planning\n"
            "2. If the question is about the current routine, provide specific feedback\n"
            "3. If the question is unrelated to the application, politely redirect to course scheduling topics\n"
            "4. Keep answers concise and focused on practical scheduling advice\n"
            "5. Format your response in clear, readable markdown\n"
        )

        response = model.generate_content(prompt)
        answer = response.text.strip()
        return jsonify({"answer": answer}), 200
    except Exception as e:
        print(f"Gemini API error during AI question answering: {e}")
        return (
            jsonify(
                {
                    "answer": "Sorry, I couldn't retrieve an answer at the moment. Please try again later.",
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/api/get_routine_feedback_ai", methods=["POST"])
def get_routine_feedback_ai():
    """Get AI feedback for a routine."""
    try:
        debugprint("\n=== Getting AI Routine Feedback ===")
        request_data = request.get_json()
        routine = request_data.get("routine", [])
        commute_preference = request_data.get("commutePreference", "")

        if not routine:
            debugprint("❌ No routine provided")
            return jsonify({"error": "No routine provided"}), 400

        debugprint(f"Getting feedback for routine with {len(routine)} sections")
        debugprint(f"Commute preference: {commute_preference}")

        feedback = get_routine_feedback_for_api(routine, commute_preference)
        debugprint("\nAI Feedback:", feedback)
        return jsonify({"feedback": feedback}), 200

    except Exception as e:
        debugprint(f"❌ Error in get_routine_feedback_ai: {e}")
        return jsonify({"error": "Failed to get AI feedback"}), 500

@app.route("/api/check_exam_conflicts_ai", methods=["POST"])
def check_exam_conflicts_ai():
    """Check for exam conflicts using AI."""
    try:
        debugprint("\n=== Checking Exam Conflicts (AI) ===")
        request_data = request.get_json()
        routine = request_data.get("routine", [])

        if not routine:
            debugprint("❌ No routine provided")
            return jsonify({"error": "No routine provided"}), 400

        debugprint(f"Checking {len(routine)} sections for exam conflicts")

        # Check AI availability
        ai_available, message = check_ai_availability()
        if not ai_available:
            debugprint(f"❌ AI not available: {message}")
            return jsonify({"error": "AI features are not available"}), 503

        # Get exam conflicts
        conflicts = check_and_return_exam_conflicts(routine)
        if conflicts:
            debugprint("\n❌ Exam conflicts found:")
            debugprint(conflicts)
            return jsonify({"conflicts": conflicts}), 200

        debugprint("\n✓ No exam conflicts found")
        return jsonify({"message": "No exam conflicts found"}), 200

    except Exception as e:
        debugprint(f"❌ Error in check_exam_conflicts_ai: {e}")
        return jsonify({"error": "Failed to check exam conflicts"}), 500


@app.route("/api/check_time_conflicts_ai", methods=["POST"])
def check_time_conflicts_ai():
    try:
        debugprint("\n=== Checking Time Conflicts (AI) ===")
        data = request.get_json()
        routine = data.get("routine", [])

        if not routine:
            debugprint("❌ No routine provided for analysis")
            return jsonify({"error": "No routine provided for analysis"}), 400

        debugprint(f"Checking {len(routine)} sections for time conflicts")

        # Check for time conflicts
        time_conflicts = []
        for i in range(len(routine)):
            section1 = routine[i]
            for j in range(i + 1, len(routine)):
                section2 = routine[j]
                debugprint(f"\nComparing {section1.get('courseCode')} with {section2.get('courseCode')}")

                # Check class schedules
                debugprint("Checking class-class conflicts...")
                for sched1 in section1.get("sectionSchedule", {}).get("classSchedules", []):
                    for sched2 in section2.get("sectionSchedule", {}).get("classSchedules", []):
                        if sched1.get("day") == sched2.get("day"):
                            start1 = TimeUtils.time_to_minutes(sched1.get("startTime"))
                            end1 = TimeUtils.time_to_minutes(sched1.get("endTime"))
                            start2 = TimeUtils.time_to_minutes(sched2.get("startTime"))
                            end2 = TimeUtils.time_to_minutes(sched2.get("endTime"))

                            if schedules_overlap(start1, end1, start2, end2):
                                debugprint(f"❌ Found class-class conflict on {sched1.get('day')}")
                                time_conflicts.append({
                                    "type": "class-class",
                                    "course1": section1.get("courseCode"),
                                    "course2": section2.get("courseCode"),
                                    "day": sched1.get("day"),
                                    "time1": f"{sched1.get('startTime')} - {sched1.get('endTime')}",
                                    "time2": f"{sched2.get('startTime')} - {sched2.get('endTime')}",
                                })

                # Check lab schedules
                debugprint("Checking lab-lab conflicts...")
                for lab1 in section1.get("labSchedules", []):
                    for lab2 in section2.get("labSchedules", []):
                        if lab1.get("day") == lab2.get("day"):
                            start1 = TimeUtils.time_to_minutes(lab1.get("startTime"))
                            end1 = TimeUtils.time_to_minutes(lab1.get("endTime"))
                            start2 = TimeUtils.time_to_minutes(lab2.get("startTime"))
                            end2 = TimeUtils.time_to_minutes(lab2.get("endTime"))

                            if schedules_overlap(start1, end1, start2, end2):
                                debugprint(f"❌ Found lab-lab conflict on {lab1.get('day')}")
                                time_conflicts.append({
                                    "type": "lab-lab",
                                    "course1": section1.get("courseCode"),
                                    "course2": section2.get("courseCode"),
                                    "day": lab1.get("day"),
                                    "time1": f"{lab1.get('startTime')} - {lab1.get('endTime')}",
                                    "time2": f"{lab2.get('startTime')} - {lab2.get('endTime')}",
                                })

                # Check lab-class and class-lab conflicts
                debugprint("Checking lab-class conflicts...")
                # Lab in section1 vs Class in section2
                for lab1 in section1.get("labSchedules", []):
                    for sched2 in section2.get("sectionSchedule", {}).get("classSchedules", []):
                        if lab1.get("day") == sched2.get("day"):
                            start1 = TimeUtils.time_to_minutes(lab1.get("startTime"))
                            end1 = TimeUtils.time_to_minutes(lab1.get("endTime"))
                            start2 = TimeUtils.time_to_minutes(sched2.get("startTime"))
                            end2 = TimeUtils.time_to_minutes(sched2.get("endTime"))

                            if schedules_overlap(start1, end1, start2, end2):
                                debugprint(f"❌ Found lab-class conflict on {lab1.get('day')}")
                                time_conflicts.append({
                                    "type": "lab-class",
                                    "course1": section1.get("courseCode"),
                                    "course2": section2.get("courseCode"),
                                    "day": lab1.get("day"),
                                    "time1": f"{lab1.get('startTime')} - {lab1.get('endTime')}",
                                    "time2": f"{sched2.get('startTime')} - {sched2.get('endTime')}",
                                })

                # Class in section1 vs Lab in section2
                debugprint("Checking class-lab conflicts...")
                for sched1 in section1.get("sectionSchedule", {}).get("classSchedules", []):
                    for lab2 in section2.get("labSchedules", []):
                        if sched1.get("day") == lab2.get("day"):
                            start1 = TimeUtils.time_to_minutes(sched1.get("startTime"))
                            end1 = TimeUtils.time_to_minutes(sched1.get("endTime"))
                            start2 = TimeUtils.time_to_minutes(lab2.get("startTime"))
                            end2 = TimeUtils.time_to_minutes(lab2.get("endTime"))

                            if schedules_overlap(start1, end1, start2, end2):
                                debugprint(f"❌ Found class-lab conflict on {sched1.get('day')}")
                                time_conflicts.append({
                                    "type": "class-lab",
                                    "course1": section1.get("courseCode"),
                                    "course2": section2.get("courseCode"),
                                    "day": sched1.get("day"),
                                    "time1": f"{sched1.get('startTime')} - {sched1.get('endTime')}",
                                    "time2": f"{lab2.get('startTime')} - {lab2.get('endTime')}",
                                })

        if not time_conflicts:
            debugprint("\n✓ No time conflicts found")
            prompt = (
                "Analyze this schedule for time management:\n"
                "• Any gaps in your schedule?\n"
                "Keep it casual and under 10 words per point.\n"
                "Start with 'Score: X/10'"
            )

            if gemini_model:
                debugprint("\nGenerating AI analysis...")
                response = gemini_model.generate_content(prompt)
                analysis = response.text.strip()
                debugprint("AI Analysis:", analysis)
            else:
                debugprint("❌ AI analysis unavailable")
                analysis = "AI analysis unavailable"

            return jsonify({"has_conflicts": False, "analysis": analysis}), 200
        else:
            debugprint(f"\n❌ Found {len(time_conflicts)} time conflicts")
            # Format the conflicts for the AI to analyze
            conflicts_text = "\n".join(
                [
                    f"- {conflict['type']} conflict between {conflict['course1']} and {conflict['course2']} on {conflict['day']}:\n  {conflict['course1']}: {conflict['time1']}\n  {conflict['course2']}: {conflict['time2']}"
                    for conflict in time_conflicts
                ]
            )
            debugprint("\nConflicts details:")
            debugprint(conflicts_text)

            prompt = (
                f"Here are your time conflicts:\n{conflicts_text}\n\n"
                "First, rate how bad these conflicts are out of 10 (10 being worst).\n"
                "Then give me 2-3 quick points:\n"
                "• How bad is it?\n"
                "• What can you do?\n"
                "Keep it casual and under 10 words per point.\n"
                "Start with 'Score: X/10'"
            )

            if gemini_model:
                debugprint("\nGenerating AI analysis of conflicts...")
                response = gemini_model.generate_content(prompt)
                analysis = response.text.strip()
                debugprint("AI Analysis:", analysis)
            else:
                debugprint("❌ AI analysis unavailable")
                analysis = "AI analysis unavailable"

            return (
                jsonify(
                    {
                        "has_conflicts": True,
                        "conflicts": time_conflicts,
                        "analysis": analysis,
                    }
                ),
                200,
            )

    except Exception as e:
        print(f"Error in check_time_conflicts_ai: {e}")
        return jsonify({"error": "Failed to analyze time conflicts"}), 500


@app.route("/api/exam_schedule")
def get_exam_schedule():
    course_code = request.args.get("courseCode")
    section_name = request.args.get("sectionName")
    if not course_code or not section_name:
        return jsonify({"error": "Missing courseCode or sectionName"}), 400

    # Find the section in the data
    for section in data:
        if section.get("courseCode") == course_code and str(
            section.get("sectionName")
        ) == str(section_name):
            # Return only the exam fields
            return jsonify(
                {
                    "courseCode": section.get("courseCode"),
                    "sectionName": section.get("sectionName"),
                    "midExamDate": section.get("midExamDate"),
                    "midExamStartTime": section.get("midExamStartTime"),
                    "midExamEndTime": section.get("midExamEndTime"),
                    "finalExamDate": section.get("finalExamDate"),
                    "finalExamStartTime": section.get("finalExamStartTime"),
                    "finalExamEndTime": section.get("finalExamEndTime"),
                }
            )
    return jsonify({"error": "Section not found"}), 404


def calculate_routine_score(
    combination, selected_days, selected_times, commute_preference
):
    """Calculate a score for a routine combination based on various factors."""
    score = 0

    # Convert selected times to minutes for easier comparison
    time_ranges = []
    for time_slot in selected_times:
        start, end = time_slot.split("-")
        start_mins = TimeUtils.time_to_minutes(start.strip())
        end_mins = TimeUtils.time_to_minutes(end.strip())
        time_ranges.append((start_mins, end_mins))

    # Score factors
    day_distribution = {day: [] for day in selected_days}  # Track classes per day
    gaps = []  # Track gaps between classes
    early_classes = 0  # Count of early morning classes
    late_classes = 0  # Count of late afternoon classes

    for section in combination:
        # Process class schedules
        if section.get("sectionSchedule") and section["sectionSchedule"].get(
            "classSchedules"
        ):
            for schedule in section["sectionSchedule"]["classSchedules"]:
                day = schedule.get("day", "").upper()
                if day in day_distribution:
                    start_time = TimeUtils.time_to_minutes(
                        schedule.get("startTime", "")
                    )
                    end_time = TimeUtils.time_to_minutes(schedule.get("endTime", ""))
                    day_distribution[day].append((start_time, end_time))

                    # Check timing preferences
                    if start_time < 540:  # Before 9:00 AM
                        early_classes += 1
                    if end_time > 960:  # After 4:00 PM
                        late_classes += 1

        # Process lab schedules
        for lab in get_lab_schedules_flat(section):
            day = lab.get("day", "").upper()
            if day in day_distribution:
                start_time = TimeUtils.time_to_minutes(lab.get("startTime", ""))
                end_time = TimeUtils.time_to_minutes(lab.get("endTime", ""))
                day_distribution[day].append((start_time, end_time))

                if start_time < 540:
                    early_classes += 1
                if end_time > 960:
                    late_classes += 1

    # Calculate scores for different factors

    # 1. Day distribution score (prefer balanced days)
    classes_per_day = [len(schedules) for schedules in day_distribution.values()]
    day_balance_score = -abs(
        max(classes_per_day) - min(classes_per_day)
    )  # Negative because we want to minimize difference
    score += day_balance_score * 2

    # 2. Gap score (minimize gaps between classes)
    for day, schedules in day_distribution.items():
        if len(schedules) > 1:
            # Sort schedules by start time
            schedules.sort(key=lambda x: x[0])
            for i in range(len(schedules) - 1):
                # Minutes between classes
                gap = schedules[i + 1][0] - schedules[i][1]
                if gap > 30:  # Only count gaps longer than 30 minutes
                    gaps.append(gap)

    if gaps:
        avg_gap = sum(gaps) / len(gaps)
        gap_score = -avg_gap / 60  # Convert to hours and make negative
        score += gap_score

    # 3. Timing preference score
    if commute_preference == "early":
        score += (5 - late_classes) * 2  # Reward fewer late classes
    elif commute_preference == "late":
        score += (5 - early_classes) * 2  # Reward fewer early classes
    else:  # balanced
        score += -abs(early_classes - late_classes) * 2  # Reward balance

    # 4. Commute preference: days on campus (OVERRIDING PRIORITY for Live Far)
    days_on_campus = sum(1 for schedules in day_distribution.values() if schedules)
    debugprint(f"Commute preference for scoring: '{commute_preference}', Days on campus: {days_on_campus}")
    
    if commute_preference == "far" or commute_preference == "Live Far":
        # For "Live Far", days on campus is the ABSOLUTE PRIORITY
        # Override all other scoring factors to ensure minimum days are selected
        
        # Calculate the theoretical minimum possible days
        all_required_days = set()
        for section in combination:
            # Get all days this section requires
            section_days = set()
            if section.get("sectionSchedule") and section["sectionSchedule"].get("classSchedules"):
                for schedule in section["sectionSchedule"]["classSchedules"]:
                    if schedule.get("day"):
                        section_days.add(schedule.get("day").upper())
            
            # Add lab days
            for lab in get_lab_schedules_flat(section):
                if lab.get("day"):
                    section_days.add(lab.get("day").upper())
            
            all_required_days.update(section_days)
        
        theoretical_min_days = len(all_required_days)
        
        # Give MASSIVE bonus for achieving the absolute minimum possible days
        if days_on_campus == theoretical_min_days:
            score += 10000  # Maximum bonus for absolute minimum
        elif days_on_campus <= theoretical_min_days + 1:
            score += 5000   # Large bonus for near-minimum
        elif days_on_campus <= 3:
            score += 2000     # Good bonus for 3 or fewer days
        else:
            score -= (days_on_campus - theoretical_min_days) * 1000  # Heavy penalty for extra days
            
        debugprint(f"Live Far scoring: theoretical_min={theoretical_min_days}, actual={days_on_campus}, score_adjustment={score}")
        
    elif commute_preference == "near" or commute_preference == "Live Near":
        # Strongly prefer routines that use all available days
        if days_on_campus == len(selected_days):
            score += 5000  # Huge bonus for using all available days
            debugprint(f"Added huge bonus for using all {len(selected_days)} available days")
        else:
            penalty = (len(selected_days) - days_on_campus) * 1000  # Heavy penalty for missing days
            score -= penalty  # Heavily penalize missing days
            debugprint(f"Applied penalty of {penalty} for missing {len(selected_days) - days_on_campus} days")
    elif commute_preference == "near" or commute_preference == "Live Near":
        # Strongly prefer routines that use all available days
        if days_on_campus == len(selected_days):
            score += 2000  # Huge bonus for using all available days
            debugprint(f"Added huge bonus for using all {len(selected_days)} available days")
        else:
            penalty = (len(selected_days) - days_on_campus) * 100
            score -= penalty  # Heavily penalize missing days
            debugprint(f"Applied penalty of {penalty} for missing {len(selected_days) - days_on_campus} days")
    else:
        # For no preference, prefer a balanced number of days
        # Ideal is roughly half the available days (rounded up)
        ideal_days = (len(selected_days) + 1) // 2
        score -= abs(days_on_campus - ideal_days) * 30  # Penalize deviation from ideal

    return score


def get_days_used_in_routine(routine):
    """Get a list of unique days used in the routine."""
    debugprint("\nGetting days used in routine")
    days_used = set()
    for section in routine:
        debugprint(f"\nProcessing section {section.get('courseCode')} {section.get('sectionName')}")
        # Check class schedules
        if section.get("sectionSchedule") and section["sectionSchedule"].get("classSchedules"):
            debugprint("Processing class schedules")
            for sched in section["sectionSchedule"]["classSchedules"]:
                if sched.get("day"):
                    day = sched["day"].upper()
                    days_used.add(day)
                    debugprint(f"Added class day: {day}")
        
        # Check lab schedules
        if section.get("labSchedules"):
            debugprint("Processing lab schedules")
            if isinstance(section["labSchedules"], list):
                for lab in section["labSchedules"]:
                    if lab.get("day"):
                        day = lab["day"].upper()
                        days_used.add(day)
                        debugprint(f"Added lab day: {day}")
            elif isinstance(section["labSchedules"], dict) and section["labSchedules"].get("classSchedules"):
                for lab_schedule in section["labSchedules"]["classSchedules"]:
                    if lab_schedule.get("day"):
                        day = lab_schedule["day"].upper()
                        days_used.add(day)
                        debugprint(f"Added lab day: {day}")
    
    days_list = sorted(list(days_used))
    debugprint(f"Total days used: {len(days_list)}")
    debugprint(f"Days: {', '.join(days_list)}")
    return days_list


def calculate_campus_days(combination):
    """Calculate the total number of unique days a student needs to be on campus."""
    debugprint("\n==== Calculating Campus Days for Combination ====")
    days = set()
    
    # Print course codes in this combination
    course_codes = [section.get('courseCode', 'Unknown') for section in combination]
    debugprint(f"Courses in combination: {', '.join(course_codes)}")
    
    for section in combination:
        if not isinstance(section, dict):
            debugprint(f"Warning: Invalid section format: {type(section)}")
            continue

        course_code = section.get('courseCode', 'Unknown')
        section_name = section.get('sectionName', 'Unknown')
        debugprint(f"\nProcessing section {course_code} {section_name}")
        
        # Check class schedules
        section_schedule = section.get("sectionSchedule", {})
        if isinstance(section_schedule, dict):
            class_schedules = section_schedule.get("classSchedules", [])
            if isinstance(class_schedules, list):
                debugprint(f"Processing {len(class_schedules)} class schedules for {course_code}")
                for schedule in class_schedules:
                    if isinstance(schedule, dict) and schedule.get("day"):
                        day = schedule["day"].upper()
                        days_before = days.copy()
                        days.add(day)
                        if day not in days_before:
                            debugprint(f"Added NEW class day: {day} for {course_code}")
                        else:
                            debugprint(f"Day {day} already counted (class for {course_code})")

        # Check lab schedules using the normalized helper function
        lab_schedules = get_lab_schedules_flat(section)
        debugprint(f"Processing {len(lab_schedules)} lab schedules for {course_code}")
        for lab_schedule in lab_schedules:
            if isinstance(lab_schedule, dict) and lab_schedule.get("day"):
                day = lab_schedule["day"].upper()
                days_before = days.copy()
                days.add(day)
                if day not in days_before:
                    debugprint(f"Added NEW lab day: {day} for {course_code}")
                else:
                    debugprint(f"Day {day} already counted (lab for {course_code})")

    days_list = sorted(list(days))
    debugprint(f"Total campus days: {len(days_list)}")
    debugprint(f"Days: {', '.join(days_list)}")
    return len(days), days_list


# Helper to normalize labSchedules to a flat array, supporting both array and object (with classSchedules) formats
def get_lab_schedules_flat(section):
    """Helper to normalize labSchedules to a flat array of schedules.
    Handles both old format (array of schedules) and new format (object with classSchedules)."""
    debugprint(f"\nGetting flat lab schedules for section {section.get('courseCode')} {section.get('sectionName')}")
    labSchedules = section.get("labSchedules")
    if not labSchedules:
        debugprint("No lab schedules found")
        return []

    # Handle old format: array of schedule objects
    if isinstance(labSchedules, list):
        debugprint("Processing old format (array of schedules)")
        schedules = [
            {
                **schedule,
                "room": section.get("labRoomName") or schedule.get("room") or "TBA",
                "faculty": section.get("labFaculties") or "TBA"
            }
            for schedule in labSchedules
        ]
        debugprint(f"Found {len(schedules)} lab schedules")
        for schedule in schedules:
            debugprint(f"Lab schedule: {schedule.get('day')} {schedule.get('startTime')}-{schedule.get('endTime')} in {schedule.get('room')}")
        return schedules

    # Handle new format: object with classSchedules array
    if isinstance(labSchedules, dict) and isinstance(labSchedules.get("classSchedules"), list):
        debugprint("Processing new format (object with classSchedules)")
        schedules = [
            {
                **schedule,
                "room": section.get("labRoomName") or schedule.get("room") or "TBA",
                "faculty": section.get("labFaculties") or "TBA"
            }
            for schedule in labSchedules["classSchedules"]
        ]
        debugprint(f"Found {len(schedules)} lab schedules")
        for schedule in schedules:
            debugprint(f"Lab schedule: {schedule.get('day')} {schedule.get('startTime')}-{schedule.get('endTime')} in {schedule.get('room')}")
        return schedules

    debugprint(f"Warning: Unrecognized lab schedule format: {type(labSchedules)}")
    return []


def convert_time_24_to_12(time_str):
    """Convert 24-hour time string to 12-hour format."""
    try:
        if not time_str:
            debugprint("Warning: Empty time string")
            return ""

        # Parse the time string
        time_parts = time_str.split(":")
        if len(time_parts) < 2:
            debugprint(f"Warning: Invalid time format: {time_str}")
            return time_str

        hours = int(time_parts[0])
        minutes = int(time_parts[1])

        # Convert to 12-hour format
        period = "AM" if hours < 12 else "PM"
        hours = hours % 12
        if hours == 0:
            hours = 12

        result = f"{hours}:{minutes:02d} {period}"
        debugprint(f"Converted {time_str} to {result}")
        return result

    except Exception as e:
        debugprint(f"Error converting time: {e}")
        return time_str

def format_section_times(section):
    """Format section times in a human-readable format."""
    try:
        debugprint(f"\nFormatting times for section {section.get('courseCode')}")
        times = []
        
        # Add class schedules
        if section.get("sectionSchedule") and section["sectionSchedule"].get("classSchedules"):
            debugprint("Processing class schedules")
            for schedule in section["sectionSchedule"]["classSchedules"]:
                start = convert_time_24_to_12(schedule.get("startTime", ""))
                end = convert_time_24_to_12(schedule.get("endTime", ""))
                day = schedule.get("day", "").title()
                if start and end and day:
                    time_str = f"{day} {start}-{end}"
                    times.append(time_str)
                    debugprint(f"Added class schedule: {time_str}")
        
        # Add lab schedules
        debugprint("Processing lab schedules")
        for lab in get_lab_schedules_flat(section):
            start = convert_time_24_to_12(lab.get("startTime", ""))
            end = convert_time_24_to_12(lab.get("endTime", ""))
            day = lab.get("day", "").title()
            if start and end and day:
                time_str = f"{day} {start}-{end} (Lab)"
                times.append(time_str)
                debugprint(f"Added lab schedule: {time_str}")
        
        debugprint(f"Formatted {len(times)} schedules")
        return times

    except Exception as e:
        debugprint(f"Error formatting section times: {e}")
        return []

def has_time_conflict(section1, section2):
    """Check if two sections have time conflicts using optimized algorithm."""
    try:
        debugprint(f"\nChecking time conflicts between {section1.get('courseCode')} and {section2.get('courseCode')}")
        
        # Get all schedules for both sections
        schedules1 = get_all_schedules(section1)
        schedules2 = get_all_schedules(section2)
        
        if not schedules1 or not schedules2:
            return False
            
        # Optimize by grouping schedules by day using hash maps
        day_schedules1 = {}
        day_schedules2 = {}
        
        # Group schedules by day for section1
        for sched in schedules1:
            day = sched.get('day', '').upper()
            if day:
                if day not in day_schedules1:
                    day_schedules1[day] = []
                day_schedules1[day].append(sched)
        
        # Group schedules by day for section2
        for sched in schedules2:
            day = sched.get('day', '').upper()
            if day:
                if day not in day_schedules2:
                    day_schedules2[day] = []
                day_schedules2[day].append(sched)
        
        # Only check days that exist in both sections
        common_days = set(day_schedules1.keys()) & set(day_schedules2.keys())
        
        for day in common_days:
            schedules_day1 = day_schedules1[day]
            schedules_day2 = day_schedules2[day]
            
            # Check for conflicts on this day
            for sched1 in schedules_day1:
                for sched2 in schedules_day2:
                    if not check_schedule_compatibility(sched1, sched2):
                        debugprint(f"Found time conflict:")
                        debugprint(f"Section 1: {section1.get('courseCode')} {sched1.get('day')} {sched1.get('startTime')}-{sched1.get('endTime')}")
                        debugprint(f"Section 2: {section2.get('courseCode')} {sched2.get('day')} {sched2.get('startTime')}-{sched2.get('endTime')}")
                        return True
        
        debugprint("No time conflicts found")
        return False

    except Exception as e:
        debugprint(f"Error checking time conflicts: {e}")
        return True  # Return True to be safe if there's an error

def get_course_details(course_code, show_all=False):
    """Get details for a specific course."""
    try:
        course_data = load_data()
        if not course_data:
            return None
            
        course_details = None
        for course in course_data:
            if course["courseCode"] == course_code:
                course_details = course
                break
                
        if not course_details:
            return None
            
        sections = course_details.get("sections", [])
        
        # Filter sections based on availability if show_all is False
        filtered_sections = []
        for section in sections:
            seats = section.get("availableSeats", 0)
            if show_all or seats > 0:
                filtered_sections.append(section)
                
        return filtered_sections
        
    except Exception as e:
        debugprint(f"Error in get_course_details: {str(e)}")
        return None

def filter_sections_by_faculty(sections, faculty):
    """Filter sections by faculty."""
    try:
        debugprint(f"\n=== Filtering Sections by Faculty: {faculty} ===")
        debugprint(f"Total sections before filtering: {len(sections)}")
        
        filtered = []
        for section in sections:
            section_faculty = section.get("faculty", "")
            section_name = section.get("sectionName", "Unknown")
            
            if section_faculty == faculty:
                debugprint(f"✓ Section {section_name} matches faculty {faculty}")
                filtered.append(section)
            else:
                debugprint(f"❌ Section {section_name} has different faculty: {section_faculty}")
                
        debugprint(f"Found {len(filtered)} sections for faculty {faculty}")
        return filtered
        
    except Exception as e:
        debugprint(f"❌ Error in filter_sections_by_faculty: {str(e)}")
        return []

if __name__ == "__main__":
    import logging
    # Enable Flask's logs for debugging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.INFO)
    
    # Run the app with debug mode disabled
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)  # Debug mode disabled

app = app
