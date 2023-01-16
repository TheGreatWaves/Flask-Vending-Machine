from app.extensions import db
from dataclasses import dataclass

@dataclass
class Machine( db.Model ):
    machine_id: int
    location: str
    
    machine_id = db.Column('machine_id', db.Integer, primary_key = True, autoincrement=True)
    location = db.Column(db.String(20), unique=True, nullable=False)
    
    def __init__(self, location):
        self.location = location
