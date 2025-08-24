from .utils import debugprint, normalize_date

def exam_schedules_overlap(exam1, exam2):
    """Check if two exam schedules conflict based on date and time."""
    try:
        # Convert times to minutes for comparison
        def convert_time(time_str):
            if not isinstance(time_str, str):
                debugprint(f"Warning: Invalid time format: {time_str}")
                return None
                
            # Remove any extra whitespace
            time_str = time_str.strip()
            
            # Handle AM/PM format
            if 'AM' in time_str.upper() or 'PM' in time_str.upper():
                try:
                    # Clean up the time string
                    time_str = time_str.upper().replace(' ', '')
                    
                    # Handle cases like "9:00AM" or "09:00AM"
                    if 'AM' in time_str:
                        time_part = time_str.replace('AM', '')
                        hours, minutes = time_part.split(':')
                        hours = int(hours)
                        if hours == 12:  # 12 AM is 00:00
                            hours = 0
                        return hours * 60 + int(minutes)
                    elif 'PM' in time_str:
                        time_part = time_str.replace('PM', '')
                        hours, minutes = time_part.split(':')
                        hours = int(hours)
                        if hours != 12:  # 12 PM stays 12, others add 12
                            hours += 12
                        return hours * 60 + int(minutes)
                except ValueError:
                    debugprint(f"Error converting 12-hour time: {time_str}")
                    return None
            
            # Try 24-hour format (HH:MM:SS)
            try:
                parts = time_str.split(':')
                hours = int(parts[0])
                minutes = int(parts[1])
                return hours * 60 + minutes
            except (ValueError, IndexError):
                debugprint(f"Error converting 24-hour time: {time_str}")
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
            
        time1 = convert_time(exam1.get("time"))
        time2 = convert_time(exam2.get("time"))
        
        if time1 is None or time2 is None:
            debugprint("Missing or invalid time information")
            return False
            
        # Assume each exam takes 2 hours
        exam_duration = 120  # minutes
        
        # Check for overlap
        end_time1 = time1 + exam_duration
        end_time2 = time2 + exam_duration
        
        overlap = max(time1, time2) < min(end_time1, end_time2)
        debugprint(f"Checking exam overlap: {time1}-{end_time1} vs {time2}-{end_time2}: {'Overlap' if overlap else 'No overlap'}")
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
            print(f"\nChecking midterm exam conflict for {schedule1['midExamDate']}:")
            print(f"{section1.get('courseCode')} vs {section2.get('courseCode')}")
            
            exam1 = {
                "date": schedule1["midExamDate"],
                "time": schedule1.get("midExamStartTime", "").replace(" ", "")
            }
            exam2 = {
                "date": schedule2["midExamDate"],
                "time": schedule2.get("midExamStartTime", "").replace(" ", "")
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
            print(f"\nChecking final exam conflict for {schedule1['finalExamDate']}:")
            print(f"{section1.get('courseCode')} vs {section2.get('courseCode')}")
            
            exam1 = {
                "date": schedule1["finalExamDate"],
                "time": schedule1.get("finalExamStartTime", "").replace(" ", "")
            }
            exam2 = {
                "date": schedule2["finalExamDate"],
                "time": schedule2.get("finalExamStartTime", "").replace(" ", "")
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