from flask import jsonify
from app.product import bp
from app.extensions import db
from app.models.product import Product

@bp.route("/create/<name>", methods=['POST'])
def create_product(name):
    
    new_product, message = Product.make(name, 100.0)

    if new_product:
        db.session.add(new_product)
        db.session.commit()

    return jsonify(
        Message=message
    )

@bp.route("/get/<identifier>", methods=['GET'])
def get_product(identifier):

    product = Product.get(identifier)

    if product:
        return jsonify(product)

    return jsonify(Error=f"Product not found!")

