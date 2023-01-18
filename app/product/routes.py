# Flask
from flask import jsonify, request
from app.product import bp
from app.extensions import db

# Models
from app.models.product import Product

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

        new_product, message = Product.make(product_name, product_price)

        if new_product:
            db.session.add(new_product)
            db.session.commit()

        return jsonify(Message=message)

    return jsonify(Message="Invalid JSON body")


@bp.route("search/<identifier>", methods=['GET'])
def search_product(identifier):

    if product := Product.find_by_name_or_id(identifier):
        return jsonify(product)

    return jsonify(Error=f"Product not found!")

@bp.route("/<int:identifier>", methods=['GET'])
def get_product(identifier):

    if product := Product.find_by_id(identifier):
        return jsonify(product)

    return jsonify(Error=f"Product not found!")


@bp.route("/<int:id>/edit", methods=['POST'])
def edit_product(id):

    # Valid product
    if product := Product.find_by_id(id):
        
        # Valid JSON body
        if content := request.get_json(): 
            new_name = content.get('name')
            new_price = content.get('price')

            changelog = product.edit(new_name=new_name, new_price=new_price)

            db.session.commit()

            return jsonify(changelog)
        
        return jsonify(Error="Invalid JSON body")

    return jsonify(Error=f"Product with ID {id} not found.")

@bp.route("/all", methods=['GET'])
def get_all_products():

    if products := Product.query.all():
        return jsonify(products)

    return jsonify(Message="There are no existing products")

@bp.route("/<int:product_id>/where", methods=['GET'])
def get_machine_with_stock(product_id):
    
    if product := Product.find_by_id(product_id):

        if machines := product.found_in():

            return jsonify(machines)

        return jsonify(Message="Product not found in any machine.")

    jsonify(Error=f"Product with ID {id} not found!")
