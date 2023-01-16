from flask import jsonify
from app.product import bp
from app.extensions import db
from app.models.product import Product

@bp.route("/create/<name>", methods=['POST'])
def create_product(name):
    new_product = Product(name)
    db.session.add(new_product)
    db.session.commit()
    return jsonify(
        Message=f"Successfully added entry for product: {name}"
    )

@bp.route("/get/<name>", methods=['GET'])
def get_product(name):
    product = Product.query.filter_by(product_name=name).first()

    if product:
        return jsonify(product)
    return jsonify(Error=f"Product with given name {name} not found!")

