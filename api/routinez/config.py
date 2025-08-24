import os
import logging
import pytz

# Global debug flag - set to True for development, False for production
DEBUG = False

# Hardcoded Google API key
GOOGLE_API_KEY = "AIzaSyC0G1uNsSKLgrGh7koSpgx4-sySYHyGoM0"

# API URLs
DATA_URL = "https://usis-cdn.eniamza.com/connect.json"

# Timezone settings
BD_TIMEZONE = pytz.timezone("Asia/Dhaka")

# Time slots (should match frontend)
TIME_SLOTS = [
    "8:00 AM-9:20 AM",
    "9:30 AM-10:50 AM",
    "11:00 AM-12:20 PM",
    "12:30 PM-1:50 PM",
    "2:00 PM-3:20 PM",
    "3:30 PM-4:50 PM",
    "5:00 PM-6:20 PM",
]

# Configure logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)