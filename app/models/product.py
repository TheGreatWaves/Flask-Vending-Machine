# Flask
import math
from app.extensions import db

# Core
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Union

# Models
from app.models.vending_machine_stock import MachineStock


@dataclass
class Product(db.Model):
    # For serializing
    product_id: int
    product_name: str
    product_price: float

    product_id = db.Column('product_id', db.Integer,
                           primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(20), unique=True, nullable=False)
    product_price = db.Column(db.DECIMAL(8, 2), nullable=False)
    machine_products = db.relationship(
        "MachineStock", backref="product", lazy=True)

    # Aliases
    OptProduct = Optional["Product"]

    def __init__(self, name, price):
        self.product_name = name
        self.product_price = price

    @staticmethod
    def find_by_id(id: int) -> OptProduct:
        return Product.query.get(id)

    @staticmethod
    def find_by_name(name: str, first: bool = False) -> Union[OptProduct, Optional[List["Product"]]]:

        exact_match = name == Product.product_name
        similar_match = Product.product_name.ilike(
            f'%{ name }%')  # ilike is case insensitive

        found = Product.query.filter(exact_match or similar_match)

        if first:
            return found.first()

        found.all()

    @staticmethod
    def find_by_name_or_id(identifier: (int | str), first: bool = False) -> Union[OptProduct, Optional[List["Product"]]]:
        if str(identifier).isnumeric():
            return Product.find_by_id(identifier)
        else:
            return Product.find_by_name(identifier, first)

    # Returns product (if success), msg (indicating success)
    @staticmethod
    def make(name: str, price: str) -> Tuple[OptProduct, str]:

        if name is None:
            return None, "Product name is missing."

        if price is None:
            return None, "Product price is missing."

        if str(name).isnumeric():
            return None, "The name cannot be a number."

        try:
            casted_price = float(price)
            if casted_price < 0.0:
                return None, "Invalid price value. (price < 0.00)"

            if Product.find_by_name(name):
                return None, "A product with the given name already exists."

            return Product(name=name, price=casted_price), f"Successfully added product: [{ name }, { casted_price }]"

        except ValueError:
            return None, f"The price value is invalid. (Incorrect type, expected float, got={type(price).__name__})"

     # Returns the change log

    def _edit_name(self, new_name: str) -> str:

        # Check redundancy
        if self.product_name == new_name:
            return "Failed, name redundant, no changes made."

        if new_name.isnumeric():
            return "Failed, the name can not be numeric."

        if Product.find_by_name(name=new_name):
            return f"Failed, an existing product with the name '{new_name}' already exists."

        log = f'{ self.product_name } -> { new_name }'
        self.product_name = new_name
        return log

    # Edits price and returns the change log
    def _edit_price(self, new_price: float):

        # Note: The exception is handled here so it
        # can bubble the error message back to the log
        try:
            # Try casting
            _casted_new_price = float(new_price)
            casted_new_price = float(f'{_casted_new_price:.2f}')

            # Check redundancy
            if math.isclose(self.product_price, casted_new_price):
                return "Failed, price redundant, no changes made"

            log = f'{ self.product_price } -> { casted_new_price }'
            self.product_price = casted_new_price
            return log

        except ValueError:
            return f"Failed, the price value is invalid. (Incorrect type, expected float, got={type(new_price).__name__})"

    # Edits the product and returns the change log
    def edit(self,
             new_name: Optional[str],
             new_price: Optional[float]
             ) -> Dict[str, str]:

        logs: Dict[str, str] = {}

        if new_name is None \
                and new_price is None:
            return {'Failed': 'Nothing to edit'}

        if new_name:
            name_log = self._edit_name(new_name=new_name)
            logs['Name'] = name_log

        if new_price:
            price_log = self._edit_price(new_price=new_price)
            logs['Price'] = price_log

        return logs

    # Returns a list of machines that the product can be found in
    # [ {id, loc, name}, ... ]
    def found_in(self) -> Optional[List[Dict[str, str]]]:

        if len(self.machine_products) == 0:
            return None

        machines: List[Dict[str, str]] = []

        for machine_stock in self.machine_products:
            machine = machine_stock.vending_machine
            entry = {
                'machine_id': machine.machine_id,
                'location': machine.location,
                'machine_name': machine.machine_name
            }
            machines.append(entry)

        return machines
