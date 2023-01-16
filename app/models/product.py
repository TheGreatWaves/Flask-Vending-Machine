from app.extensions import db
from dataclasses import dataclass
from app.models.vending_machine_stock import MachineStock
from typing import List

@dataclass
class Product( db.Model ):
    product_id: int
    product_name: str
    product_price: float
    machine_products: List[ MachineStock ]

    product_id = db.Column( 'product_id', db.Integer, primary_key = True, autoincrement=True )
    product_name = db.Column( db.String(20), unique=True, nullable=False)
    product_price = db.Column( db.DECIMAL(10, 2), nullable=False )
    machine_products = db.relationship( "MachineStock", backref="product", lazy=True )

    def __init__(self, name):
        self.product_name = name