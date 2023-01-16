from app.extensions import db
from dataclasses import dataclass

@dataclass
class Product( db.Model ):
    product_id: int
    product_name: str

    product_id = db.Column('product_id', db.Integer, primary_key = True, autoincrement=True)
    product_name = db.Column(db.String(20), unique=True, nullable=False)

    def __init__(self, name):
        self.product_name = name