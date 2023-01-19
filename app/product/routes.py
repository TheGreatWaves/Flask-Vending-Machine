# Flask
from flask import jsonify, request
from app.product import bp
from app.extensions import db

# Models
from app.models.product import Product

# Utils
from app.utils import common
from app.utils.log import Log

"""
Expected JSON:
{
    "name": <str>,
    "price": <float>
}
"""

@bp.route("/create", methods=['POST'])
def create_product():

    if content := request.get_json():

        product_name = content.get('product_name')
        product_price = content.get('product_price')

        result = Product.make(product_name, product_price)

        if result.object:
            db.session.add(result.object)
            db.session.commit()

        return jsonify(Log().addResult("Product", f"New Product: {product_name}, {product_price}", result, Product.ERROR_CREATE_FAIL))

    return jsonify(common.JSON_ERROR)


@bp.route("/search/<identifier>", methods=['GET'])
def search_product(identifier):

    if product := Product.find_by_name_or_id(identifier):
        return jsonify(product)

    return jsonify(Log().error(Product.ERROR_NOT_FOUND, f"Product not found. (Identifier: {identifier})"))

@bp.route("/<int:product_id>", methods=['GET'])
def get_product(product_id):

    if product := Product.find_by_id(product_id):
        return jsonify(product)

    return jsonify(Log().error(Product.ERROR_NOT_FOUND, f"Product not found. (Product ID: {product_id})"))


@bp.route("/<int:product_id>/edit", methods=['POST'])
def edit_product(product_id):

    # Valid product
    if product := Product.find_by_id(product_id):
        
        # Valid JSON body
        if content := request.get_json(): 
            new_name = content.get('product_name')
            new_price = content.get('product_price')

            changelog = product.edit(new_name=new_name, new_price=new_price)

            db.session.commit()

            return jsonify(changelog)
        
        return jsonify(common.JSON_ERROR)

    return jsonify(Log().error(Product.ERROR_NOT_FOUND, f"Product not found. (Product ID: {product_id})"))

@bp.route("/all", methods=['GET'])
def get_all_products():

    if products := Product.query.all():
        return jsonify(products)

    return jsonify(Log().error(Product.ERROR_NOT_FOUND, "There are no existing products"))

@bp.route("/<int:product_id>/where", methods=['GET'])
def get_machine_with_stock(product_id):
    
    if product := Product.find_by_id(product_id):

        if machines := product.found_in():

            return jsonify(machines)

        return jsonify(Log().error(Product.ERROR_NOT_FOUND, "Product not found in any machine."))


    return jsonify(Log().error(Product.ERROR_NOT_FOUND, f"Product not found. (Product ID: {product_id})"))
