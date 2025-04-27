from flask import Flask, request, jsonify, g
from service import TranslationService, UserService
from models import Schema
import sqlite3
import os
import json

app = Flask(__name__)

API_KEY_HEADER = 'X-API-Key'
DATABASE = os.environ.get('DATABASE_PATH', 'translations.db')

def get_db():
    """Function to get the database for later use
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Ensure rows are dictionary-like
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Function to close the connection to a database
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Function to get the database for later use
def get_translation_service():
    """Function to get the translation service
    """
    return TranslationService(get_db())

def get_user_service():
    """Function to get the user service
    """
    return UserService(get_db())

def authenticate():
    """Function to authenticate a users API key to ensure safe data transfer
    """
    api_key = request.headers.get(API_KEY_HEADER)
    if api_key:
        user_service = get_user_service()
        user = user_service.get_user_by_api_key(api_key)
        if user:
            return True
    return False

def requires_auth(func):
    """Wrapper function to determine what routes need to be authenticated
    """
    def wrapper(*args, **kwargs):
        if authenticate():
            return func(*args, **kwargs) #pass the proper arguments to authenticate
        else:
            return jsonify({"error": "Unauthorized"}), 401 #Unautorized error if not found
    wrapper.__name__ = func.__name__
    return wrapper

@app.after_request
def add_headers(response):
   """Function to add proper headers
    """
   response.headers['Access-Control-Allow-Origin'] = "*"
   response.headers['Access-Control-Allow-Headers'] =  "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
   response.headers['Access-Control-Allow-Methods']=  "POST, GET, PUT, DELETE, OPTIONS"
   return response

@app.route("/")
def hello():
   return "Hello World!"

@app.route("/register", methods=["POST"])
def register():
    """Route to add a user to the database and get an API Key
    """
    user_data = request.get_json()
    if not user_data or not user_data.get("username") or not user_data.get("password"):
        return jsonify({"error": "Missing username or password"}), 400
    user_service = get_user_service()
    new_user = user_service.register_user(user_data)
    if new_user:
        return jsonify({"id": new_user['id'], "username": new_user['username'], "api_key": new_user['api_key']}), 201
    else:
        return jsonify({"error": "Username already exists"}), 409

@app.route("/translations", methods=["GET"])
@requires_auth
def list_translations():
   translation_service = get_translation_service()
   return jsonify(translation_service.list())


@app.route("/translations", methods=["POST"])
@requires_auth
def create_translation():
   translation_service = get_translation_service()
   return jsonify(translation_service.create(request.get_json()))


@app.route("/translations/<item_id>", methods=["PUT"])
@requires_auth
def update_item(item_id):
   translation_service = get_translation_service()
   return jsonify(translation_service.update(item_id, request.get_json()))

@app.route("/translations/<item_id>", methods=["GET"])
@requires_auth
def get_item(item_id):
   translation_service = get_translation_service()
   return jsonify(translation_service.get_by_id(item_id))

@app.route("/translations/<item_id>", methods=["DELETE"])
@requires_auth
def delete_item(item_id):
   translation_service = get_translation_service()
   return jsonify(translation_service.delete(item_id))


if __name__ == "__main__":
   Schema()
   app.run(debug=True, host='0.0.0.0', port=5000)
