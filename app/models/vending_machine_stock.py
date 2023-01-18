# Flask
from app.extensions import db

# Core
from dataclasses import dataclass
from typing import Tuple, Optional, List, Dict

# Models
from app.models import product, vending_machine

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

    # Aliases
    Quantity = int
    ProductID = int
    OptStock = Optional[ "MachineStock" ]
    StockInfo = Tuple[ ProductID, Quantity ]
    ListOfStockInfo = List[ StockInfo ]

    @staticmethod
    def get( machine_id: int, product_id: int ) -> OptStock:
        return MachineStock.query.filter_by( machine_id=machine_id, product_id=product_id ).first()

    @staticmethod
    def make( machine_id: int, product_id: ( int|str ), quantity: int ) -> Tuple[ OptStock, str ]:
        
        if vending_machine.Machine.find_by_id( machine_id ) is None:
            return None, f"No machine with id { machine_id } found."

        target_product = product.Product.find_by_name_or_id( identifier=product_id, first=True )
        if target_product is None:
            return None, f"No product with id/name { product_id } found."

        if quantity <= 0:
            return None, f"Invalid quantity. ( n <= 0 )"

        # Prevent duplicate entry
        if MachineStock.get( machine_id=machine_id, product_id=product_id, ):
            return None, f"An existing entry already exists for machine { machine_id } and product { target_product.product_id }"

        return MachineStock( 
            machine_id=machine_id, 
            product_id=target_product.product_id, 
            quantity=quantity
            ), \
            f"Added product { target_product.product_id } to machine { machine_id } successfully"

    @property
    def product_name( self ):
        return self.product.product_name

    @property
    def product_price( self ):
        return self.product.product_price

    """
    Processes the following json body into a list of tuples ( pid, quantity )

    [
        {
            "product_id": <product_id>,
            "quantity": <quantity>
        },
        ...
    ]
    """
    @staticmethod
    def process_raw( raw: Optional[ List[ Dict[ str, str ] ] ] ) -> Optional[ ListOfStockInfo ]:
        
        if raw is None:
            return None
        
        stock_information_list: MachineStock.ListOfStockInfo = []

        for stock_info in raw:
            product_id = stock_info.get('product_id')
            quantity = stock_info.get('quantity')
            stock_information_list.append( ( product_id, quantity ) )

        return stock_information_list

    def remove_from_machine(self):
        db.session.delete(self)

    def decrease_stock(self):
        self.quantity -= 1
    
    def add_stock(self):
        self.quantity += 1

    def out_of_stock(self) -> bool:
        return self.quantity == 0

        