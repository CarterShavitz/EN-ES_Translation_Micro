from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

# Import the translation model
try:
    from translation_model import get_translation_model
    from simple_translator import get_simple_translator
    TRANSLATION_MODEL_AVAILABLE = True
except ImportError:
    print("Warning: Translation model dependencies not installed. Machine translation will not be available.")
    TRANSLATION_MODEL_AVAILABLE = False

app = Flask(__name__)
# Enable CORS for all routes with support for credentials and custom headers
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "X-API-Key"]}}, supports_credentials=True)

API_KEY_HEADER = 'X-API-Key'
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://user-service:5001')

@app.after_request
def add_headers(response):
    """Function to add proper headers"""
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Access-Control-Allow-Headers'] = "Content-Type, X-API-Key, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] = "POST, GET, PUT, DELETE, OPTIONS"
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route("/translate", methods=["OPTIONS"])
def options_translate():
    """Handle OPTIONS requests for CORS preflight"""
    response = jsonify({"status": "ok"})
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Access-Control-Allow-Headers'] = "Content-Type, X-API-Key, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] = "POST, GET, PUT, DELETE, OPTIONS"
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

def authenticate(api_key):
    """Function to authenticate a user's API key by calling the user service"""
    if not api_key:
        return False

    try:
        response = requests.get(
            f"{USER_SERVICE_URL}/validate-key",
            headers={"X-API-Key": api_key}
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return False

def requires_auth(func):
    """Wrapper function to determine what routes need to be authenticated"""
    def wrapper(*args, **kwargs):
        api_key = request.headers.get(API_KEY_HEADER)
        if authenticate(api_key):
            return func(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    wrapper.__name__ = func.__name__
    return wrapper

@app.route("/api")
def hello():
    """Simple API health check endpoint"""
    return "Translation API is running!"

@app.route("/translate", methods=["POST"])
@requires_auth
def translate_text():
    """Translate English text to Spanish using the ML model"""
    if not TRANSLATION_MODEL_AVAILABLE:
        return jsonify({"error": "Translation model is not available"}), 503

    data = request.get_json()
    if not data or not data.get("text"):
        return jsonify({"error": "Missing text to translate"}), 400

    text = data.get("text")

    try:
        # Get the translation model and translate the text
        model = get_translation_model()
        translation = model.translate(text)

        return jsonify({"translation": translation})
    except Exception as e:
        # Fallback to simple translator if ML model fails
        try:
            simple_model = get_simple_translator()
            translation = simple_model.translate(text)
            return jsonify({"translation": translation, "note": "Used fallback translator"})
        except Exception as simple_e:
            return jsonify({"error": f"Translation failed: {str(e)}, Fallback also failed: {str(simple_e)}"}), 500

if __name__ == "__main__":
    # Initialize translation model if available
    if TRANSLATION_MODEL_AVAILABLE:
        try:
            # Load the model in a separate thread to avoid blocking the app startup
            import threading
            threading.Thread(target=get_translation_model, daemon=True).start()
            print("Translation model loading in background...")
        except Exception as e:
            print(f"Error loading translation model: {e}")

    app.run(debug=True, host='0.0.0.0', port=5002)
