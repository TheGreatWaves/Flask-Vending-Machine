from app.extensions import db
from dataclasses import dataclass

@dataclass
class MachineStock( db.Model ):
    machine_id : int
    product_id : int
    quantity: int

    machine_id = db.Column( db.Integer, db.ForeignKey('machine.machine_id'), primary_key=True )
    product_id = db.Column( db.Integer, db.ForeignKey('product.product_id'), primary_key=True )
    quantity = db.Column( db.Integer, nullable=False )
