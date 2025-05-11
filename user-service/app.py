from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
import os
import uuid
import bcrypt

app = Flask(__name__)
# Enable CORS for all routes with support for credentials and custom headers
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "X-API-Key"]}}, supports_credentials=True)

API_KEY_HEADER = 'X-API-Key'
DATABASE = os.environ.get('DATABASE_PATH', 'data/users.db')

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
        CREATE TABLE IF NOT EXISTS "user" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            api_key TEXT UNIQUE
        )
        ''')
        db.commit()

@app.after_request
def add_headers(response):
    """Function to add proper headers"""
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Access-Control-Allow-Headers'] = "Content-Type, X-API-Key, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] = "POST, GET, PUT, DELETE, OPTIONS"
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route("/register", methods=["OPTIONS"])
def options_register():
    """Handle OPTIONS requests for CORS preflight"""
    response = jsonify({"status": "ok"})
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Access-Control-Allow-Headers'] = "Content-Type, X-API-Key, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] = "POST, GET, PUT, DELETE, OPTIONS"
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route("/validate-key", methods=["OPTIONS"])
def options_validate_key():
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
    return "User Management API is running!"

@app.route("/register", methods=["POST"])
def register():
    """Route to add a user to the database and get an API Key"""
    user_data = request.get_json()
    if not user_data or not user_data.get("username") or not user_data.get("password"):
        return jsonify({"error": "Missing username or password"}), 400

    username = user_data.get("username")
    password = user_data.get("password")

    # Hash the password
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    # Generate API key
    api_key = str(uuid.uuid4())

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO user (username, password_hash, api_key) VALUES (?, ?, ?)",
            (username, hashed_password, api_key)
        )
        db.commit()

        # Get the user data
        cursor.execute("SELECT id, username, api_key FROM user WHERE username = ?", (username,))
        row = cursor.fetchone()

        return jsonify({
            "id": row["id"],
            "username": row["username"],
            "api_key": row["api_key"]
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409

@app.route("/validate-key", methods=["GET"])
def validate_key():
    """Validate an API key"""
    api_key = request.headers.get(API_KEY_HEADER)
    if not api_key:
        return jsonify({"error": "No API key provided"}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username FROM user WHERE api_key = ?", (api_key,))
    row = cursor.fetchone()

    if row:
        return jsonify({"valid": True, "user_id": row["id"], "username": row["username"]}), 200
    else:
        return jsonify({"valid": False, "error": "Invalid API key"}), 401

@app.route("/users", methods=["GET"])
def list_users():
    """List all users (admin only)"""
    # In a real application, this would require admin authentication
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username FROM user")
    rows = cursor.fetchall()

    result = [{column: row[i] for i, column in enumerate(["id", "username"])} for row in rows]
    return jsonify(result)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)
