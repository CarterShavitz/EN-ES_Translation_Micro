from flask import Flask, request, jsonify
from service import TranslationService
from models import Schema

import json

app = Flask(__name__)


@app.after_request
def add_headers(response):
   response.headers['Access-Control-Allow-Origin'] = "*"
   response.headers['Access-Control-Allow-Headers'] =  "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
   response.headers['Access-Control-Allow-Methods']=  "POST, GET, PUT, DELETE, OPTIONS"
   return response

@app.route("/")
def hello():
   return "Hello World!"

@app.route("/translations", methods=["GET"])
def list_translations():
   return jsonify(TranslationService().list())


@app.route("/translations", methods=["POST"])
def create_translation():
   return jsonify(TranslationService().create(request.get_json()))


@app.route("/translations/<item_id>", methods=["PUT"])
def update_item(item_id):
   return jsonify(TranslationService().update(item_id, request.get_json()))

@app.route("/translations/<item_id>", methods=["GET"])
def get_item(item_id):
   return jsonify(TranslationService().get_by_id(item_id))

@app.route("/translations/<item_id>", methods=["DELETE"])
def delete_item(item_id):
   return jsonify(TranslationService().delete(item_id))


if __name__ == "__main__":
   Schema()
   app.run(debug=True, host='0.0.0.0', port=5000)
