from app.extensions import db
from dataclasses import dataclass

# Vending machine
@dataclass
class Machine( db.Model ):
    machine_id: int
    name: str

    machine_id = db.Column('user_id', db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    
    def __init__(self, name):
        self.name = name
