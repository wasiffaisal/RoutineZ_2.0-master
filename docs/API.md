# RoutineZ API Documentation

## Overview

The RoutineZ API is a Flask-based backend service that provides comprehensive course scheduling functionality for BRAC University students. It integrates with Google's Gemini AI for intelligent schedule optimization and offers real-time data from BracU Connect.

## Base URL
```
https://routinez-api.vercel.app
```

## Authentication
All endpoints are public and do not require authentication. However, rate limiting is enforced to ensure fair usage.

## Rate Limiting
- **Standard Rate**: 100 requests per minute per IP
- **Extended Rate**: 1000 requests per hour per IP
- **Burst Protection**: Temporary blocks for excessive requests

## Response Format
All API responses follow a consistent JSON format:

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "status": "error",
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## API Endpoints

### 1. Health Check
Check the status of the API and its dependencies.

**Endpoint:** `GET /api/connapi-status`

**Response:**
```json
{
  "status": "online",
  "ai_available": true,
  "ai_message": "AI service is operational",
  "debug_mode": false,
  "version": "2.0.0",
  "uptime": "99.9%"
}
```

### 2. Get All Courses
Retrieve comprehensive course data including sections, faculty, and schedules.

**Endpoint:** `GET /api/courses`

**Response:**
```json
{
  "data": [
    {
      "course_code": "CSE110",
      "course_name": "Structured Programming Language",
      "credit": 3,
      "sections": [
        {
          "section": "1",
          "faculty": "Dr. John Doe",
          "faculty_rating": 4.5,
          "schedule": {
            "day": "MW",
            "time": "08:00-09:30",
            "room": "AC2-301",
            "building": "AC2"
          },
          "available_seats": 45,
          "total_seats": 50,
          "waitlist": 3,
          "lab_schedule": {
            "day": "F",
            "time": "14:00-16:00",
            "room": "Lab-201"
          }
        }
      ],
      "mid_exam": {
        "date": "2024-03-15",
        "time": "09:00-11:00",
        "room": "TBA"
      },
      "final_exam": {
        "date": "2024-04-20",
        "time": "14:00-17:00",
        "room": "TBA"
      },
      "prerequisites": [],
      "description": "Introduction to structured programming concepts"
    }
  ]
}
```

### 3. Check Schedule Conflicts
Analyze selected course sections for conflicts.

**Endpoint:** `POST /api/check-conflicts`

**Request Body:**
```json
{
  "selected_sections": [
    {
      "course_code": "CSE110",
      "section": "1",
      "faculty": "Dr. John Doe"
    },
    {
      "course_code": "MAT110",
      "section": "2",
      "faculty": "Dr. Jane Smith"
    }
  ]
}
```

**Response:**
```json
{
  "conflicts": [
    {
      "type": "time",
      "severity": "high",
      "courses": ["CSE110", "MAT110"],
      "details": "Classes overlap on Monday 08:00-09:30",
      "resolution": "Consider CSE110 Section 2 or MAT110 Section 1"
    },
    {
      "type": "exam",
      "severity": "medium",
      "courses": ["CSE110", "PHY110"],
      "details": "Mid-term exams scheduled on same day",
      "resolution": "Exams are 3 hours apart - manageable"
    }
  ],
  "has_conflicts": true,
  "total_conflicts": 2,
  "compatibility_score": 0.75
}
```

### 4. AI Schedule Optimization
Generate AI-powered schedule suggestions based on user preferences.

**Endpoint:** `POST /api/ai-suggest`

**Request Body:**
```json
{
  "prompt": "Generate an optimal schedule for 5 courses with no classes before 9 AM",
  "preferences": {
    "preferred_days": ["MWF", "TT"],
    "time_slots": ["09:00-10:30", "11:00-12:30", "14:00-15:30"],
    "commute_preference": "near",
    "max_daily_classes": 3,
    "preferred_faculty": ["Dr. John Doe", "Dr. Jane Smith"],
    "avoid_early_morning": true,
    "optimize_gaps": true
  },
  "selected_courses": ["CSE110", "MAT110", "PHY110"],
  "temperature": 0.7
}
```

**Response:**
```json
{
  "suggestion": "Based on your preferences, here's an optimized schedule:",
  "optimized_schedule": [
    {
      "course_code": "CSE110",
      "section": "2",
      "faculty": "Dr. John Doe",
      "schedule": {
        "day": "MW",
        "time": "09:00-10:30"
      },
      "confidence": 0.92
    }
  ],
  "optimization_factors": {
    "commute_time": "Reduced by 30%",
    "daily_balance": "Evenly distributed",
    "faculty_rating": "Average 4.3/5",
    "gap_optimization": "Minimal waiting time"
  },
  "alternative_schedules": [
    {
      "description": "Early morning option",
      "schedule": [...],
      "trade_offs": ["Earlier classes", "Better faculty"]
    }
  ]
}
```

### 5. Get Course Details
Retrieve detailed information about a specific course.

**Endpoint:** `GET /api/course-details?course=CSE110`

**Response:**
```json
{
  "course_code": "CSE110",
  "course_name": "Structured Programming Language",
  "credit": 3,
  "description": "Introduction to structured programming concepts",
  "prerequisites": [],
  "corequisites": [],
  "sections": [
    {
      "section": "1",
      "faculty": "Dr. John Doe",
      "faculty_rating": 4.5,
      "schedule": {
        "lecture": {
          "day": "MW",
          "time": "08:00-09:30",
          "room": "AC2-301"
        },
        "lab": {
          "day": "F",
          "time": "14:00-16:00",
          "room": "Lab-201"
        }
      },
      "enrollment": {
        "available": 45,
        "total": 50,
        "waitlist": 3
      }
    }
  ],
  "exams": {
    "mid": {
      "date": "2024-03-15",
      "time": "09:00-11:00",
      "format": "Written",
      "coverage": "Chapters 1-6"
    },
    "final": {
      "date": "2024-04-20",
      "time": "14:00-17:00",
      "format": "Written + Practical",
      "coverage": "Comprehensive"
    }
  }
}
```

## Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `COURSE_NOT_FOUND` | Requested course doesn't exist | Check course code spelling |
| `INVALID_SECTION` | Section number is invalid | Verify section exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry later |
| `AI_SERVICE_UNAVAILABLE` | AI service temporarily down | Try again in a few minutes |
| `DATA_SOURCE_ERROR` | Unable to fetch course data | Check API status endpoint |
| `VALIDATION_ERROR` | Invalid request format | Check request body structure |

## Rate Limiting Headers

Responses include rate limiting information:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

## SDK Examples

### JavaScript/Node.js
```javascript
// Fetch all courses
const response = await fetch('https://routinez-api.vercel.app/api/courses');
const data = await response.json();

// Check conflicts
const conflicts = await fetch('https://routinez-api.vercel.app/api/check-conflicts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    selected_sections: [
      { course_code: 'CSE110', section: '1' }
    ]
  })
});
```

### Python
```python
import requests

# Get all courses
response = requests.get('https://routinez-api.vercel.app/api/courses')
courses = response.json()['data']

# Check conflicts
conflicts = requests.post('https://routinez-api.vercel.app/api/check-conflicts', 
    json={
        'selected_sections': [
            {'course_code': 'CSE110', 'section': '1'}
        ]
    }
).json()
```

### cURL
```bash
# Get courses
curl https://routinez-api.vercel.app/api/courses

# Check conflicts
curl -X POST https://routinez-api.vercel.app/api/check-conflicts \
  -H "Content-Type: application/json" \
  -d '{"selected_sections": [{"course_code": "CSE110", "section": "1"}]}'
```

## WebSocket Support (Future)
Coming soon: Real-time updates via WebSocket for:
- Live seat availability changes
- Schedule conflict alerts
- AI suggestion updates

## Changelog

### Version 2.0.0
- Added AI-powered schedule optimization
- Enhanced conflict detection with resolution suggestions
- Improved response formats with additional metadata
- Added compatibility scoring
- New `/course-details` endpoint

### Version 1.5.0
- Added rate limiting protection
- Improved error handling
- Added health check endpoint
- Enhanced data validation

### Version 1.0.0
- Initial API release
- Basic course and section endpoints
- Simple conflict detection
- AI integration for suggestions