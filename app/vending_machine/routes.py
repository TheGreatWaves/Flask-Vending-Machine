from app.vending_machine import bp
from flask import jsonify, request
from app.extensions import db

from app.models.vending_machine import Machine
from app.models.product import Product
from app.models.vending_machine_stock import MachineStock

from typing import Optional

@bp.route( '/create/<location>/<name>', methods=['POST'] )
def create( location, name ):
    machine, message = Machine.make( location, name )

    if machine:
        db.session.add( machine )
        db.session.commit()

    return jsonify( Message=message )

@bp.route( "/at/<location>", methods=['GET'], defaults={ 'name': None } )
@bp.route( "at/<location>/<name>", methods=['GET'] )
def get( location, name ):

    if machine := Machine.find( location=location, name=name ):
        return jsonify( machine )
    else:
        return jsonify( Error=f"No machine found. ( Location: { location }, Name: { name } )" )

@bp.route( "<machine_id>/add/<product_identifier>", methods=['POST'] )
def add_product_to_machine( machine_id: int, product_identifier: (int | str) ):

    if target_machine := Machine.find_by_id( machine_id ):
        stock, message = target_machine.add_product( product_identifier=product_identifier, quantity=10 )

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
@bp.route( "/<id>/edit", methods=['POST'] )
def edit_machine( id ):

    # Valid machine
    if machine := Machine.find_by_id( id ): 

        # Existing json body
        if content := request.get_json():

            # Returns the value if found from request body (json) else None
            get_if_found = lambda name : None if name not in content else content[ name ]
            
            name = get_if_found( 'name' )
            location = get_if_found( 'location' )
            stock_list = get_if_found( 'stock_list' ) # Type: Optional[ List[ Dict[ str, str ] ] ]

            stock_information_list = MachineStock.process_raw( stock_list )

            # Even if all these are None, it will not break.
            val = machine.edit(
                new_name=name,
                new_location=location,
                new_stock=stock_information_list
            )

            db.session.commit()

            # Return log info
            return jsonify( Log=val )

    return jsonify( Error="Invalid JSON body")

    
    

