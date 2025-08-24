from flask import Flask
import os

from .config import DEBUG
from .utils import debugprint
from .data_loader import load_data
from .ai_service import initialize_ai
from .routes import app as flask_app

def create_app():
    """Create and configure the Flask application."""
    # Initialize AI service
    ai_initialized = initialize_ai()
    if ai_initialized:
        debugprint("AI service initialized successfully")
    else:
        debugprint("Failed to initialize AI service")
    
    # Preload data
    data = load_data()
    if data:
        debugprint(f"Successfully preloaded {len(data)} course sections")
    else:
        debugprint("Failed to preload course data")
    
    # Return the Flask app instance from routes.py
    return flask_app

# Create the application instance
app = create_app()

# Run the app if this file is executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=DEBUG)