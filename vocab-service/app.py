from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
import os
import requests

app = Flask(__name__)
# Enable CORS for all routes with support for credentials and custom headers
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "X-API-Key"]}}, supports_credentials=True)

API_KEY_HEADER = 'X-API-Key'
DATABASE = os.environ.get('DATABASE_PATH', 'data/vocab.db')
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://user-service:5001')

def get_db():
    """Function to get the database for later use"""
    db = getattr(g, '_database', None)
    if db is None:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Ensure rows are dictionary-like
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Function to close the connection to a database"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with the required tables"""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "en_es" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            English TEXT,
            Spanish TEXT
        )
        ''')
        db.commit()

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

@app.after_request
def add_headers(response):
    """Function to add proper headers"""
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Access-Control-Allow-Headers'] = "Content-Type, X-API-Key, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] = "POST, GET, PUT, DELETE, OPTIONS"
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route("/translations", methods=["OPTIONS"])
def options_translations():
    """Handle OPTIONS requests for CORS preflight"""
    response = jsonify({"status": "ok"})
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Access-Control-Allow-Headers'] = "Content-Type, X-API-Key, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] = "POST, GET, PUT, DELETE, OPTIONS"
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route("/api")
def hello():
    """Simple API health check endpoint"""
    return "Vocabulary API is running!"

@app.route("/translations", methods=["GET"])
@requires_auth
def list_translations():
    """List all vocabulary entries"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, English, Spanish FROM en_es")
    rows = cursor.fetchall()
    result = [{column: row[i] for i, column in enumerate(["id", "English", "Spanish"])} for row in rows]
    return jsonify(result)

@app.route("/translations", methods=["POST"])
@requires_auth
def create_translation():
    """Create a new vocabulary entry"""
    data = request.get_json()
    if not data or not data.get("English") or not data.get("Spanish"):
        return jsonify({"error": "Missing English or Spanish term"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO en_es (English, Spanish) VALUES (?, ?)",
        (data.get("English"), data.get("Spanish"))
    )
    db.commit()

    # Get the inserted item
    item_id = cursor.lastrowid
    cursor.execute("SELECT id, English, Spanish FROM en_es WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    result = {column: row[i] for i, column in enumerate(["id", "English", "Spanish"])}

    return jsonify(result), 201

@app.route("/translations/<int:item_id>", methods=["PUT"])
@requires_auth
def update_item(item_id):
    """Update a vocabulary entry"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    updates = []
    params = []

    if "English" in data:
        updates.append("English = ?")
        params.append(data["English"])

    if "Spanish" in data:
        updates.append("Spanish = ?")
        params.append(data["Spanish"])

    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    params.append(item_id)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"UPDATE en_es SET {', '.join(updates)} WHERE id = ?",
        params
    )
    db.commit()

    # Get the updated item
    cursor.execute("SELECT id, English, Spanish FROM en_es WHERE id = ?", (item_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "Item not found"}), 404

    result = {column: row[i] for i, column in enumerate(["id", "English", "Spanish"])}
    return jsonify(result)

@app.route("/translations/<int:item_id>", methods=["GET"])
@requires_auth
def get_item(item_id):
    """Get a specific vocabulary entry"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, English, Spanish FROM en_es WHERE id = ?", (item_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "Item not found"}), 404

    result = {column: row[i] for i, column in enumerate(["id", "English", "Spanish"])}
    return jsonify(result)

@app.route("/translations/<int:item_id>", methods=["DELETE"])
@requires_auth
def delete_item(item_id):
    """Delete a vocabulary entry"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM en_es WHERE id = ?", (item_id,))
    db.commit()

    return jsonify({"message": "Item deleted successfully"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
