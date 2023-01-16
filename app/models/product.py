from app.extensions import db
from dataclasses import dataclass
from app.models.vending_machine_stock import MachineStock
from typing import List, Tuple, Optional

@dataclass
class Product( db.Model ):
    product_id: int
    product_name: str
    product_price: float
    machine_products: List[ MachineStock ]

    product_id = db.Column( 'product_id', db.Integer, primary_key = True, autoincrement=True )
    product_name = db.Column( db.String(20), unique=True, nullable=False)
    product_price = db.Column( db.DECIMAL(8, 2), nullable=False )
    machine_products = db.relationship( "MachineStock", backref="product", lazy=True )

    def __init__( self, name, price ):
        self.product_name = name
        self.product_price = price

    @classmethod
    def findByID( cls, id ) -> Optional[ "Product" ]:
        return Product.query.get( id )

    @classmethod
    def findByName( cls, name ) -> Optional[ "Product" ]:
        # Note: ilike the 'i' indicates case INSENSITIVE
        return Product.query.filter( (Product.product_name == name) | (Product.product_name.ilike(f'%{ name }%')) ).first()

    @classmethod
    def get( cls, identifier ) -> Optional[ "Product" ]:
        if identifier.isdigit():
            return Product.findByID( identifier )
        else:
            return Product.findByName( identifier )

    @classmethod
    def make( cls, name, price ) -> Tuple[ Optional[ "Product" ], str ]:

        if name.isdigit():
            return None, "The name cannot be a number."
        
        if Product.findByName( name ):
            return None, "A product with the given name already exists."

        if price < 0.0:
            return None, "Invalid price value."

        return Product( name=name, price=price ), f"Successfully added product: [{ name }, { price }]"

        

        

    
