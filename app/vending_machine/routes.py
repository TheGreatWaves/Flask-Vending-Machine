# Flask
from app.vending_machine import bp
from flask import jsonify, request
from app.extensions import db

# Models
from app.models.vending_machine import Machine
from app.models.product import Product
from app.models.vending_machine_stock import MachineStock


@bp.route("/create/<location>/<name>", methods=["POST"])
def create(location, name):
    machine, message = Machine.make(location, name)

    if machine:
        db.session.add(machine)
        db.session.commit()

    return jsonify(Message=message)


@bp.route("/at/<location>", methods=["GET"], defaults={"name": None})
@bp.route("/at/<location>/<name>", methods=["GET"])
def get(location, name):

    if machine := Machine.find(location=location, name=name):
        return jsonify(machine)
    else:
        return jsonify(
            Error=f"No machine found. ( Location: { location }, Name: { name } )"
        )


# TODO: make this be able to add several
@bp.route("/<int:machine_id>/add", methods=["POST"])
def add_product_to_machine(machine_id: int):

    if target_machine := Machine.find_by_id(machine_id):

        if content := request.get_json():

            raw_stock_list = content.get('stock_list')
            stock_list = MachineStock.process_raw(raw_stock_list)
            log = target_machine.add_products(stocks=stock_list)
            
            db.session.commit()

            return jsonify(log)

        return jsonify(Message="Invalid JSON body.")

    return jsonify(Message=f"No machine found with given id { machine_id }.")


@bp.route("/<int:id>", methods=["GET"])
def get_machine_by_id(id):

    if machine := Machine.find_by_id(id):
        return jsonify(machine)

    return jsonify(Error=f"No machine with given ID {id} found.")


"""
Important NOTE:

We expect the json body in the form of:
{
    "name": <machine_name>,
    "location": <location>,
    "stock_list": [
        {
            "product_id": <product_id>,
            "quantity": <quantity>
        },
        ...
    ]
}
"""


@bp.route("/<int:id>/edit", methods=["POST"])
def edit_machine(id):

    # Valid machine
    if machine := Machine.find_by_id(id):

        # Valid JSON body
        if content := request.get_json():

            new_name = content.get("name")
            new_location = content.get("location")
            # Type: Optional[ List[ Dict[ str, str ] ] ]
            new_stock_list = content.get("stock_list")

            stock_information_list = MachineStock.process_raw(new_stock_list)

            # Even if all these are None, it will not break.
            changelog = machine.edit(
                new_name=new_name, new_location=new_location, new_stock=stock_information_list
            )

            db.session.commit()

            # Return log info
            return jsonify(Log=changelog)

        return jsonify(Error="Invalid JSON body")

    return jsonify(Error=f'No machine with given ID ({id}) found')


@bp.route("/all", methods=["GET"])
def get_all_machines():

    if machines := Machine.query.all():
        return jsonify(machines)

    return jsonify(Message="There are no existing machines")


@bp.route("/<int:machine_id>/buy/<int:product_id>", methods=["POST"])
def buy_product_from_machine(machine_id: int, product_id: (int | str)):

    if target_machine := Machine.find_by_id(machine_id):

        # Valid JSON body
        if content := request.get_json():

            payment: float = content.get('payment')

            change, message = target_machine.buy_product(
                product_id=product_id, payment=payment)

            return jsonify(
                Change=change,
                Message=message
            )

        return jsonify(Message="Invalid JSON")

    return jsonify(Message=f"No machine found with given id { machine_id }.")


@bp.route("/<int:machine_id>/remove/<product_id>", methods=["GET"])
def remove_product_from_machine(machine_id: int, product_id: (int | str)):

    if target_machine := Machine.find_by_id(machine_id):

        target_machine.remove_stock(product_id=product_id)
        db.session.commit()

        return jsonify(Message=f"Product ID {product_id} removed from machine ID {machine_id}.")

    return jsonify(Message=f"No machine found with given id { machine_id }.")
