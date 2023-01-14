# Flask imports
from flask import jsonify
from init_schema import *

#=========================================#
#   START OF ENTRY POINT INITIALIZATION   #
#=========================================#

@app.route("/", methods=['GET'])
def index():
    return jsonify(
        Message="Vending machine goes brr",
    )

@app.route('/create/<name>', methods=['POST'])
def create(name):
    machine = Machine(name)
    db.session.add(machine)
    db.session.commit()
    return jsonify(Message=f"Successfully created {name}!")

@app.route("/get/<name>", methods=['GET'])
def get(name):
    machine = Machine.query.filter_by(name=name).first()

    if machine:
        return jsonify(machine)
    else:
        return jsonify(Error="Machine with given name not found.")

#=========================================#
#    END OF ENTRY POINT INITIALIZATION    #
#=========================================#



