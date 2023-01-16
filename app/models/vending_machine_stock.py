from app.extensions import db
from dataclasses import dataclass
from typing import Tuple, Optional
from app.models import product, vending_machine
from sqlalchemy.ext.hybrid import hybrid_property

"""
This represents the relationship between
the machines and the products they have.
"""
@dataclass
class MachineStock( db.Model ):
    # For serializing 
    # machine_id: int
    product_id: int
    product_name: str
    product_price: float
    quantity: int

    machine_id = db.Column( db.Integer, db.ForeignKey('machine.machine_id'), primary_key=True )
    product_id = db.Column( db.Integer, db.ForeignKey('product.product_id'), primary_key=True )
    quantity = db.Column( db.Integer, nullable=False )

    @staticmethod
    def get( machine_id: int, product_id: int ) -> Optional[ "MachineStock" ]:
        return MachineStock.query.filter_by( machine_id=machine_id, product_id=product_id ).first()

    @staticmethod
    def make( machine_id: int, product_identifier: ( int|str ), quantity: int ) -> Tuple[ Optional[ "MachineStock" ], str ]:
        
        if vending_machine.Machine.find_by_id( machine_id ) is None:
            return None, f"No machine with id { machine_id } found."

        target_product = product.Product.find_by_name_or_id( product_identifier )
        if target_product is None:
            return None, f"No product with id/name { product_identifier } found."

        if quantity <= 0:
            return None, f"Invalid quantity. ( n <= 0 )"

        # Prevent duplicate entry
        if MachineStock.get( machine_id=machine_id, product_id=target_product.product_id, ):
            return None, f"An existing entry already exists for machine { machine_id } and product { target_product.product_id }"

        return MachineStock( 
            machine_id=machine_id, 
            product_id=target_product.product_id, 
            quantity=quantity
            ), \
            f"Added product to machine { machine_id } successfully"

    @property
    def product_name( self ):
        return self.product.product_name

    @property
    def product_price( self ):
        return self.product.product_price
