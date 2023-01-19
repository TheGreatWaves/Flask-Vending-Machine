# Flask
from app.vending_machine import bp
from flask import jsonify, request
from app.extensions import db

# Models
from app.models.vending_machine import Machine
from app.models.product import Product
from app.models.vending_machine_stock import MachineStock

# Utils
from app.utils.log import Log

@bp.route("/create/<location>/<name>", methods=["POST"])
def create(location, name):

    log = Log()

    result = Machine.make(location, name)
    machine, _ = result
    
    if machine:
        db.session.add(machine)
        db.session.commit()

    log.addResult("Machine", f"New Machine: {location}, {name}", result, Machine.ERROR_CREATE_FAIL)

    return jsonify(log)


@bp.route("/at/<location>", methods=["GET"], defaults={"name": None})
@bp.route("/at/<location>/<name>", methods=["GET"])
def get(location, name):

    if machine := Machine.find(location=location, name=name):
        return jsonify(machine)
    else:
        return jsonify(
            Log().error(Machine.ERROR_NOT_FOUND, f"No machine found. (Location: { location }, Name: { name })")
        )

"""
Note: This class is ABLE to add multiple products at once
Expects: Json{ 'stock_list':[ {product_id:<int>, quantity:<int>}, ... ] }
"""
@bp.route("/<int:machine_id>/add", methods=["POST"])
def add_product_to_machine(machine_id: int):

    if target_machine := Machine.find_by_id(machine_id):

        if content := request.get_json():

            raw_stock_list = content.get('stock_list')
            stock_list = MachineStock.process_raw(raw_stock_list)
            log = target_machine.add_products(stocks=stock_list)
            
            db.session.commit()

            return jsonify(log)

        return jsonify(Log().error("JSON Error", "Invalid JSON body."))

    return jsonify(Log().error(Machine.ERROR_NOT_FOUND, f"No machine found with given id { machine_id }."))


@bp.route("/<int:id>", methods=["GET"])
def get_machine_by_id(id):

    if machine := Machine.find_by_id(id):
        return jsonify(machine)

    return jsonify( Log().error(Machine.ERROR_NOT_FOUND, f"No machine with given ID {id} found."))

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
            return jsonify(changelog)

        return jsonify(Log().error("JSON Error", "Invalid JSON body"))

    return jsonify(Log().error(Machine.ERROR_NOT_FOUND, f'No machine with given ID ({id}) found'))


@bp.route("/all", methods=["GET"])
def get_all_machines():

    if machines := Machine.query.all():
        return jsonify(machines)

    return jsonify(Log().error(Machine.ERROR_NOT_FOUND, "There are no existing machines"))


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

        return jsonify(Log().error("JSON Error", "Invalid JSON body"))

    return jsonify(Log().error(Machine.ERROR_NOT_FOUND, f"No machine found with given id { machine_id }."))


@bp.route("/<int:machine_id>/remove/<product_id>", methods=["POST"])
def remove_product_from_machine(machine_id: int, product_id: str):

    if target_machine := Machine.find_by_id(machine_id):

        result = target_machine.remove_stock(product_id=product_id)

        if result.success:
            db.session.commit()

        return jsonify(Log().addResult("Machine", f"Machine ID {machine_id}", result, Machine.ERROR_REMOVE_PRODUCT))

    return jsonify(Log().error(Machine.ERROR_NOT_FOUND, f"No machine found with given id { machine_id }."))

@bp.route("/<int:machine_id>/destroy", methods=["POST"])
def remove_machine(machine_id):

    if target_machine := Machine.find_by_id(machine_id):

        target_machine.destroy()
        db.session.commit()
        return jsonify(Log().add("Machine", f"Machine ID {machine_id}", "Successfully delelted."))

    return jsonify(Log().error(Machine.ERROR_NOT_FOUND, f"No machine found with given id { machine_id }."))
