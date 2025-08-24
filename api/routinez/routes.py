from flask import Flask, request, jsonify
from flask_cors import CORS
import json

from .config import DEBUG
from .utils import debugprint
from .data_loader import load_data
from .ai_service import check_ai_availability, generate_ai_response
from .exam_utils import ExamConflictChecker

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Store data globally
data = None

@app.route('/api/connapi-status', methods=['GET'])
def connapi_status():
    """Check the status of the connection API."""
    debugprint("\n=== Checking API Status ===")
    ai_available, ai_message = check_ai_availability()
    
    return jsonify({
        "status": "online",
        "ai_available": ai_available,
        "ai_message": ai_message,
        "debug_mode": DEBUG
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working."""
    return jsonify({"message": "API is working!"})

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses data."""
    global data
    
    # Load data if not already loaded
    if data is None:
        data = load_data()
    
    # If data is still None after trying to load, return error
    if data is None:
        return jsonify({"error": "Failed to load course data"}), 500
    
    return jsonify({"data": data})

@app.route('/api/check-conflicts', methods=['POST'])
def check_conflicts():
    """Check for conflicts between selected course sections."""
    global data
    
    # Load data if not already loaded
    if data is None:
        data = load_data()
    
    # If data is still None after trying to load, return error
    if data is None:
        return jsonify({"error": "Failed to load course data"}), 500
    
    try:
        request_data = request.get_json()
        selected_sections = request_data.get('selected_sections', [])
        
        if not selected_sections:
            return jsonify({"error": "No sections provided"}), 400
        
        # Create conflict checker instance
        conflict_checker = ExamConflictChecker(data)
        
        # Check for conflicts
        conflicts = conflict_checker.check_conflicts(selected_sections)
        
        return jsonify({
            "conflicts": conflicts,
            "has_conflicts": len(conflicts) > 0
        })
    except Exception as e:
        debugprint(f"Error checking conflicts: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai-suggest', methods=['POST'])
def ai_suggest():
    """Generate AI suggestions based on user input."""
    try:
        request_data = request.get_json()
        prompt = request_data.get('prompt', '')
        temperature = request_data.get('temperature', 0.7)
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Generate AI response
        response = generate_ai_response(prompt, temperature)
        
        return jsonify(response)
    except Exception as e:
        debugprint(f"Error generating AI suggestion: {e}")
        return jsonify({"error": str(e)}), 500