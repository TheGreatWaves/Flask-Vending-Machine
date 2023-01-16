from app.extensions import db
from dataclasses import dataclass
from app.models.product import Product
from app.models.vending_machine_stock import MachineStock
from typing import List, Optional, Tuple

@dataclass
class Machine( db.Model ):
    # For serializing 
    machine_id: int
    location: str
    products: List[ MachineStock ]
    
    machine_id = db.Column( 'machine_id', db.Integer, primary_key = True, autoincrement=True )
    location = db.Column( db.String( 20 ), unique=False, nullable=False )
    products = db.relationship( "MachineStock", backref="vending_machine", lazy=True )
    
    def __init__( self, location ):
        self.location = location

    @staticmethod
    def make( location: str, products: Optional[ List[Product] ] = None) -> Tuple[ Optional[ "Machine" ], str ]:

        new_machine = Machine( location=location )
        
        if products:
            for product in products:
                stock, message = new_machine.add_product( product.product_id )

                if stock is None:
                    return None, message
        
        return new_machine, f"Successfully created entry for vending machine at { location }!"
        

    @staticmethod
    def find_by_id( id ) -> Optional[ "Machine" ]:
        return Machine.query.get( id )


    # Returns ALL machines at indicated location
    @staticmethod
    def find_by_location( location ) -> Optional[ List[ "Machine" ] ]:

        exact_match = Machine.location == location
        similar_match =  Machine.location.ilike(f'%{ location }%') # ilike is case insensitive

        return Machine.query.filter( exact_match or similar_match ).all()

    def add_product( self, product_identifier: ( int|str ), quantity: int ) -> Tuple[ Optional[ "MachineStock" ], str ]:
        return MachineStock.make( machine_id=self.machine_id, product_identifier=product_identifier, quantity=quantity )