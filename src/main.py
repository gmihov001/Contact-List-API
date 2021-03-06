"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os, json
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Contact
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/contacts', methods=['GET'])
def get_all_contacts():
    contacts = Contact.query.all()
    contacts = list(map(lambda x:x.serialize(), contacts))
    return jsonify(contacts), 200

@app.route('/contacts/<int:id>', methods=['GET'])
def get_one_contact(id):
    contact = Contact.query.get(id)
    contact = list(map(lambda x:x.serialize(), contact))
    return jsonify(contact), 200

@app.route('/contacts', methods=['POST'])
def add_contact():
    body = request.json
    new_contact = Contact(full_name=body["full_name"], email=body["email"], phone=body["phone"], address=body["address"])
    db.session.add(new_contact)
    contacts = Contact.query.all()
    contacts = list(map(lambda x:x.serialize(), contacts))
    return jsonify(contacts), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
