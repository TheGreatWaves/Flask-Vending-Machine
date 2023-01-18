from app.extensions import db
from dataclasses import dataclass
from app.models.vending_machine_stock import MachineStock
from typing import List, Tuple, Optional, Dict

@dataclass
class Product( db.Model ):
    # For serializing 
    product_id: int
    product_name: str
    product_price: float

    product_id = db.Column( 'product_id', db.Integer, primary_key = True, autoincrement=True )
    product_name = db.Column( db.String(20), unique=True, nullable=False)
    product_price = db.Column( db.DECIMAL(8, 2), nullable=False )
    machine_products = db.relationship( "MachineStock", backref="product", lazy=True )

    def __init__( self, name, price ):
        self.product_name = name
        self.product_price = price

    @staticmethod
    def find_by_id( id: int ) -> Optional[ "Product" ]:
        return Product.query.get( id )

    @staticmethod
    def find_by_name( name: str ) -> Optional[ "Product" ]:
        
        exact_match = name == Product.product_name
        similar_match = Product.product_name.ilike(f'%{ name }%') # ilike is case insensitive

        return Product.query.filter( exact_match or similar_match ).first()

    @staticmethod
    def find_by_name_or_id( identifier: (int | str) ) -> Optional[ "Product" ]:
        if str(identifier).isnumeric():
            return Product.find_by_id( identifier )
        else:
            return Product.find_by_name( identifier )

    @staticmethod
    def make( name: str, price: float ) -> Tuple[ Optional[ "Product" ], str ]:

        if name is int and name.isdigit():
            return None, "The name cannot be a number."
        
        if Product.find_by_name( name ):
            return None, "A product with the given name already exists."

        if price < 0.0:
            return None, "Invalid price value."

        return Product( name=name, price=price ), f"Successfully added product: [{ name }, { price }]"

        

    
