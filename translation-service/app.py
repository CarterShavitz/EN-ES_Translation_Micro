from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import re

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
VOCAB_SERVICE_URL = os.environ.get('VOCAB_SERVICE_URL', 'http://vocab-service:5000')

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

def fetch_vocabulary(api_key):
    """Fetch vocabulary terms from the vocab service"""
    try:
        response = requests.get(
            f"{VOCAB_SERVICE_URL}/translations",
            headers={"X-API-Key": api_key}
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch vocabulary: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching vocabulary: {str(e)}")
        return []

def preprocess_text(text, vocabulary):
    """Replace vocabulary terms with their definitions in the text"""
    if not vocabulary:
        return text

    # Create a dictionary mapping English terms to their definitions
    vocab_dict = {}
    for item in vocabulary:
        # In the vocab service, English is the term (e.g., "SOW") and Spanish is the definition (e.g., "Scope of Work")
        term = item.get("English", "").strip()
        definition = item.get("Spanish", "").strip()
        if term and definition:
            vocab_dict[term] = definition

    if not vocab_dict:
        return text

    # Sort terms by length (longest first) to handle cases where one term is a substring of another
    sorted_terms = sorted(vocab_dict.keys(), key=len, reverse=True)

    # Create a pattern to match whole words only, case-insensitive
    pattern = r'\b(?:' + '|'.join(re.escape(term) for term in sorted_terms) + r')\b'

    def replace_term(match):
        term = match.group(0)
        # Get the original case of the term
        original_term = term
        # Get the definition from the dictionary (case-insensitive lookup)
        for vocab_term, definition in vocab_dict.items():
            if vocab_term.lower() == term.lower():
                # Preserve the original capitalization if possible
                if original_term.isupper():
                    # All uppercase, keep definition as is or uppercase it if needed
                    return definition.upper() if original_term == original_term.upper() else definition
                elif original_term[0].isupper():
                    # First letter uppercase, capitalize the definition
                    return definition[0].upper() + definition[1:] if definition else definition
                else:
                    # Lowercase, keep definition as is
                    return definition
        return original_term

    # Replace all occurrences of terms with their definitions, case-insensitive
    processed_text = re.sub(pattern, replace_term, text, flags=re.IGNORECASE)

    return processed_text

@app.route("/api")
def hello():
    """Simple API health check endpoint"""
    return "Translation API is running!"

@app.route("/translate", methods=["POST"])
@requires_auth
def translate_text():
    """Translate English text to Spanish using the ML model with vocabulary preprocessing"""
    if not TRANSLATION_MODEL_AVAILABLE:
        return jsonify({"error": "Translation model is not available"}), 503

    data = request.get_json()
    if not data or not data.get("text"):
        return jsonify({"error": "Missing text to translate"}), 400

    original_text = data.get("text")
    api_key = request.headers.get(API_KEY_HEADER)

    # Fetch vocabulary terms
    vocabulary = fetch_vocabulary(api_key)

    # Preprocess text by replacing terms with their definitions
    preprocessed_text = preprocess_text(original_text, vocabulary)

    # Log the preprocessing results for debugging
    print(f"Original text: {original_text}")
    print(f"Preprocessed text: {preprocessed_text}")

    # Track if preprocessing made changes
    preprocessing_applied = original_text != preprocessed_text

    try:
        # Get the translation model and translate the preprocessed text
        model = get_translation_model()
        translation = model.translate(preprocessed_text)

        response = {
            "translation": translation,
            "preprocessed": preprocessing_applied
        }

        # If preprocessing was applied, include the preprocessed text in the response
        if preprocessing_applied:
            response["preprocessed_text"] = preprocessed_text

        return jsonify(response)
    except Exception as e:
        # Fallback to simple translator if ML model fails
        try:
            simple_model = get_simple_translator()
            translation = simple_model.translate(preprocessed_text)

            response = {
                "translation": translation,
                "preprocessed": preprocessing_applied,
                "note": "Used fallback translator"
            }

            # If preprocessing was applied, include the preprocessed text in the response
            if preprocessing_applied:
                response["preprocessed_text"] = preprocessed_text

            return jsonify(response)
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
