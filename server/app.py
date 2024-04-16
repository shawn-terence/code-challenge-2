#!/usr/bin/env python3

from models import db, Sweet, Vendor, VendorSweet
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Code challenge</h1>'

#get vendors
@app.route('/vendors')
def get_vendors():
    vendors = Vendor.query.all()
    vendors_data = [{"id": vendor.id, "name": vendor.name} for vendor in vendors]
    return jsonify(vendors_data)

#get vendors using id
# GET /vendors/<int:id>
@app.route('/vendors/<int:id>')
def get_vendor(id):
    vendor = Vendor.query.get(id)
    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404

    vendor_data = {
        "id": vendor.id,
        "name": vendor.name,
        "vendor_sweets": [
            {
                "id": vs.id,
                "price": vs.price,
                "sweet": {
                    "id": vs.sweet.id,
                    "name": vs.sweet.name
                },
                "sweet_id": vs.sweet_id,
                "vendor_id": vs.vendor_id
            }
            for vs in vendor.vendor_sweets
        ]
    }
    return jsonify(vendor_data)

# GET /sweets
@app.route('/sweets')
def get_sweets():
    sweets = Sweet.query.all()
    sweets_data = [{"id": sweet.id, "name": sweet.name} for sweet in sweets]
    return jsonify(sweets_data)

# GET /sweets/<int:id>
@app.route('/sweets/<int:id>')
def get_sweet(id):
    sweet = Sweet.query.get(id)
    if not sweet:
        return jsonify({"error": "Sweet not found"}), 404

    sweet_data = {
        "id": sweet.id,
        "name": sweet.name
    }
    return jsonify(sweet_data)

# POST /vendor_sweets
@app.route('/vendor_sweets', methods=['POST'])
def create_vendor_sweet():
    data = request.json
    if not all(key in data for key in ['price', 'vendor_id', 'sweet_id']):
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        vendor_sweet = VendorSweet(price=data['price'], vendor_id=data['vendor_id'], sweet_id=data['sweet_id'])
        db.session.add(vendor_sweet)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 500

    response_data = {
        "id": vendor_sweet.id,
        "price": vendor_sweet.price,
        "sweet": {
            "id": vendor_sweet.sweet.id,
            "name": vendor_sweet.sweet.name
        },
        "sweet_id": vendor_sweet.sweet_id,
        "vendor": {
            "id": vendor_sweet.vendor.id,
            "name": vendor_sweet.vendor.name
        },
        "vendor_id": vendor_sweet.vendor_id
    }
    return jsonify(response_data), 201

# DELETE /vendor_sweets/<int:id>
@app.route('/vendor_sweets/<int:id>', methods=['DELETE'])
def delete_vendor_sweet(id):
    vendor_sweet = VendorSweet.query.get(id)
    if not vendor_sweet:
        return jsonify({"error": "VendorSweet not found"}), 404

    try:
        db.session.delete(vendor_sweet)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 500

    return jsonify({}), 204

if __name__ == '__main__':
    app.run(port=5555, debug=True)