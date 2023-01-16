from app.extensions import db
from dataclasses import dataclass
from app.models.vending_machine_stock import MachineStock
from typing import List

@dataclass
class Machine( db.Model ):
    machine_id: int
    location: str
    products: List[ MachineStock ]    
    
    machine_id = db.Column( 'machine_id', db.Integer, primary_key = True, autoincrement=True )
    location = db.Column( db.String( 20 ), unique=True, nullable=False )
    products = db.relationship( "MachineStock", backref="vending_machine", lazy=True )
    
    def __init__( self, location ):
        self.location = location
