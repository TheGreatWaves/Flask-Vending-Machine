from app.vending_machine import bp
from flask import jsonify
from app.extensions import db
from app.models.vending_machine import Machine

@bp.route('/create/<name>', methods=['POST'])
def create(name):
    machine = Machine(name)
    db.session.add(machine)
    db.session.commit()
    return jsonify(Message=f"Successfully created {name}!")

@bp.route("/get/<name>", methods=['GET'])
def get(name):
    machine = Machine.query.filter_by(name=name).first()

    if machine:
        return jsonify(machine)
    else:
        return jsonify(Error="Machine with given name not found.")