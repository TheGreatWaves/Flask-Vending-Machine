from app.vending_machine import bp
from flask import jsonify
from app.extensions import db

from app.models.vending_machine import Machine
from app.models.product import Product

@bp.route( '/create/<location>', methods=['POST'] )
def create( location ):
    machine, message = Machine.make( location )

    if machine:
        db.session.add( machine )
        db.session.commit()

    return jsonify( Message=message )

@bp.route( "/at/<location>", methods=['GET'] )
def get( location ):
    if machine := Machine.find_by_location( location=location ):
        return jsonify( machine )
    else:
        return jsonify( Error=f"No machine found at given location. ({ location })" )

@bp.route( "<machine_id>/add/<product_identifier>", methods=['POST'] )
def add_product_to_machine( machine_id: int, product_identifier: (int | str) ):

    if target_machine := Machine.find_by_id( machine_id ):
        stock, message = target_machine.add_product(  product_identifier=product_identifier, quantity=10 )

        if stock:
            db.session.add( stock )
            db.session.commit()
            
        return jsonify( Message=message )

    return jsonify( Message=f"No machine found with given id { machine_id }.")
    

@bp.route( "/<id>", methods=['GET'] )
def get_machine_by_id( id ):

    if machine := Machine.find_by_id( id ):
        return jsonify( machine )

    return jsonify( Error=f"No machine with given ID {id} found." )



    
    

