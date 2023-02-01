from flask import Response, jsonify, request

from app.extensions import db
from app.models.vending_machine import Machine
from app.models.vending_machine_stock import MachineStock
from app.utils import common
from app.utils.log import Log
from app.vending_machine import bp


@bp.route("/create/<location>/<name>", methods=["POST"])
def create(location: str, name: str) -> Response:
    log = Log()

    result = Machine.make(location, name)
    machine, _ = result

    if machine:
        db.session.add(machine)
        db.session.commit()

    log.add_result(
        name="Machine",
        specific=f"New Machine: {location}, {name}",
        result=result,
        err_name=Machine.ERROR_CREATE_FAIL,
    )

    return jsonify(log)


@bp.route("/at/<location>", methods=["GET"], defaults={"name": None})
@bp.route("/at/<location>/<name>", methods=["GET"])
def get(location: str, name: str) -> Response:
    if machine := Machine.find(location=location, name=name):
        return jsonify(machine)
    else:
        return jsonify(
            Log().error(
                Machine.ERROR_NOT_FOUND,
                f"No machine found. (Location: {location}, Name: {name})",
            )
        )


"""
Note: This class is ABLE to add multiple products at once
Expects: Json{ 'stock_list':[ {product_id:<int>, quantity:<int>}, ... ] }
"""


@bp.route("/<int:machine_id>/add", methods=["POST"])
def add_product_to_machine(machine_id: int) -> Response:
    target_machine, machine_not_found_msg = Machine.find_by_id(machine_id)
    if target_machine:

        if content := request.get_json():
            raw_stock_list = content.get("stock_list")
            stock_list = MachineStock.process_raw(raw_stock_list)
            log = target_machine.add_products(stocks=stock_list)

            db.session.commit()

            return jsonify(log)

        return jsonify(common.JSON_ERROR)

    return jsonify(Log().error(Machine.ERROR_NOT_FOUND, machine_not_found_msg))


@bp.route("/<int:machine_id>", methods=["GET"])
def get_machine_by_id(machine_id: int) -> Response:
    machine, machine_not_found_msg = Machine.find_by_id(machine_id)
    if machine:
        return jsonify(machine)

    return jsonify(Log().error(Machine.ERROR_NOT_FOUND, machine_not_found_msg))


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


@bp.route("/<int:machine_id>/edit", methods=["POST"])
def edit_machine(machine_id: int) -> Response:
    machine, machine_not_found_msg = Machine.find_by_id(machine_id)
    # Valid machine
    if machine:

        # Valid JSON body
        if content := request.get_json():
            new_name = content.get("machine_name")
            new_location = content.get("location")
            # Type: Optional[ List[ Dict[ str, str ] ] ]
            new_stock_list = content.get("stock_list")

            stock_information_list = MachineStock.process_raw(new_stock_list)

            # Even if all these are None, it will not break.
            changelog = machine.edit(
                new_name=new_name,
                new_location=new_location,
                new_stock=stock_information_list,
            )

            db.session.commit()

            # Return log info
            return jsonify(changelog)

        return jsonify(common.JSON_ERROR)

    return jsonify(Log().error(Machine.ERROR_NOT_FOUND, machine_not_found_msg))


@bp.route("/all", methods=["GET"])
def get_all_machines() -> Response:
    machines = Machine.query.all()
    if machines:
        return jsonify(machines)

    return jsonify(
        Log().error(Machine.ERROR_NOT_FOUND, "There are no existing machines")
    )


@bp.route("/<int:machine_id>/buy/<int:product_id>", methods=["POST"])
def buy_product_from_machine(machine_id: int, product_id: (int | str)) -> Response:
    target_machine, machine_not_found_msg = Machine.find_by_id(machine_id)

    if target_machine:

        # Valid JSON body
        if content := request.get_json():
            payment: float = content.get("payment")

            purchase_log = target_machine.buy_product(
                product_id=product_id, payment=payment
            )

            return jsonify(purchase_log)

        return jsonify(common.JSON_ERROR)

    return jsonify(Log().error(Machine.ERROR_NOT_FOUND, machine_not_found_msg))


@bp.route("/<int:machine_id>/remove/<product_id>", methods=["POST"])
def remove_product_from_machine(machine_id: int, product_id: str) -> Response:
    target_machine, machine_not_found_msg = Machine.find_by_id(machine_id)
    if target_machine:

        result = target_machine.remove_stock(product_id=product_id)

        if result.object:
            db.session.commit()

        return jsonify(
            Log().add_result(
                "Machine",
                f"Machine ID {machine_id}",
                result,
                Machine.ERROR_REMOVE_PRODUCT,
            )
        )

    return jsonify(Log().error(Machine.ERROR_NOT_FOUND, machine_not_found_msg))


@bp.route("/<int:machine_id>/destroy", methods=["POST"])
def remove_machine(machine_id: int) -> Response:
    target_machine, machine_not_found_msg = Machine.find_by_id(machine_id)

    if target_machine:
        msg = target_machine.destroy()
        db.session.commit()
        return jsonify(Log().add("Machine", f"Machine ID {machine_id}", msg))

    return jsonify(Log().error(Machine.ERROR_NOT_FOUND, machine_not_found_msg))
