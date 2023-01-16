from app.vending_machine import bp
from flask import jsonify
from app.extensions import db
from app.models.vending_machine import Machine

@bp.route('/create/<location>', methods=['POST'])
def create(location):
    machine = Machine(location)
    db.session.add(machine)
    db.session.commit()
    return jsonify(Message=f"Successfully created entry for vending machine at {location}!")

@bp.route("/get/<location>", methods=['GET'])
def get(location):
    machine = Machine.query.filter_by(location=location).first()

    if machine:
        return jsonify(machine)
    else:
        return jsonify(Error="Machine at given location not found.")