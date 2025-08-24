import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from .config import GOOGLE_API_KEY
from .utils import debugprint

# Initialize Gemini model
gemini_model = None
gemini_configured = False

def initialize_ai():
    """Initialize the AI service with the Google Gemini API."""
    global gemini_model, gemini_configured
    
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
        return True
    except ImportError as ie:
        print(f"✗ ImportError configuring Gemini: {ie}")
        print("✗ Warning: google.generativeai package not installed. AI features will be disabled.")
        return False
    except Exception as e:
        print(f"✗ Failed to configure Gemini API: {str(e)}")
        print(f"Error type: {type(e)}")
        gemini_model = None
        return False

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

def generate_ai_response(prompt, temperature=0.7):
    """Generate a response using the Gemini AI model."""
    if not gemini_configured or not gemini_model:
        return {"error": "AI service not available"}
    
    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
        )
        
        return {
            "text": response.text,
            "status": "success"
        }
    except Exception as e:
        debugprint(f"Error generating AI response: {e}")
        return {
            "error": str(e),
            "status": "error"
        }