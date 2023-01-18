# Flask
from app.extensions import db

# Core
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

# Models
from app.models.product import Product
from app.models.vending_machine_stock import MachineStock


@dataclass
class Machine(db.Model):
    # For serializing
    machine_id: int
    machine_name: str
    location: str
    products: List[MachineStock]

    machine_id = db.Column('machine_id', db.Integer,
                           primary_key=True, autoincrement=True)
    machine_name = db.Column(db.String(20), unique=True, nullable=False)
    location = db.Column(db.String(20), unique=False, nullable=False)
    products = db.relationship(
        "MachineStock", backref="vending_machine", lazy=True)

    # Aliases
    ListOfMachines = List["Machine"]
    OptMachine = Optional["Machine"]

    @staticmethod
    def make(location: str, name: str, products: Optional[MachineStock.ListOfStockInfo] = None) -> Tuple[OptMachine, str]:

        if Machine.find(name=name, location=location):
            return None, f"A machine with given name and location already exists. (Location: { location }, Name: { name })"

        new_machine = Machine(location=location, machine_name=name)

        if products:
            for product in products:
                stock, message = new_machine.add_product(product.product_id)

                if stock is None:
                    return None, message

        return new_machine, f"Successfully created entry for vending machine at { location }!"

    @staticmethod
    def find_by_id(id) -> OptMachine:
        return Machine.query.get(id)

    @staticmethod
    def __find_by_name(name: str):
        return Machine.query.filter_by(machine_name=name)

    @staticmethod
    def find_by_name(name: str) -> OptMachine:
        return Machine.__find_by_name(name=name).first()

    @staticmethod
    def __find_by_location(location):

        exact_match = Machine.location == location
        similar_match = Machine.location.ilike(
            f'%{ location }%')  # ilike is case insensitive

        return Machine.query.filter(exact_match or similar_match)

    @staticmethod
    def find_by_location(location) -> Optional[ListOfMachines]:
        return Machine.__find_by_location(location=location).all()

    @staticmethod
    def find(name: Optional[str] = None, location: Optional[str] = None) -> Union[OptMachine, Optional[ListOfMachines]]:

        # Nothing given
        if name is None and location is None:
            return None

        # Only name given
        if name and location:
            return Machine.__find_by_location(location=location).filter_by(machine_name=name).first()

        if location:
            return Machine.find_by_location(location=location)

        if name:
            return Machine.find_by_name(name=name)

    def add_product(self, product_identifier: (int | str), quantity: int) -> Tuple[MachineStock.OptStock, str]:
        return MachineStock.make(machine_id=self.machine_id, product_identifier=product_identifier, quantity=quantity)

    # Returns the change log
    def _edit_name(self, new_name: str) -> str:

        # Check redundancy
        if self.machine_name == new_name:
            return "Redundant, no changes made"

        log = f'{ self.machine_name } -> { new_name }'
        self.machine_name = new_name
        return log

    # Returns the change log
    def _edit_location(self, new_location: str):

        # Check redundancy
        if self.location == new_location:
            return "Redundant, no changes made"

        log = f'{ self.location } -> { new_location }'
        self.location = new_location
        return log

    # Returns the whole change log
    def edit(self,
             new_name: Optional[str],
             new_location: Optional[str],
             new_stock: Optional[MachineStock.ListOfStockInfo]
             ) -> Dict[str, str]:

        logs: Dict[str, str] = {}

        if new_name is None \
                and new_location is None \
                and new_stock is None:
            return {'Failed': 'Nothing to edit'}

        if new_name:
            name_log = self._edit_name(new_name=new_name)
            logs['Name'] = name_log

        if new_location:
            location_log = self._edit_location(new_location=new_location)
            logs['Location'] = location_log

        if new_stock:

            # Expect success by default
            logs['Stock'] = "Successfully editted stock"

            # Delete current stock
            delete_stock = MachineStock.__table__.delete().where(
                MachineStock.machine_id == self.machine_id)
            db.session.execute(delete_stock)

            # Add all new stock
            for product_id, quantity in new_stock:
                stock_info, message = self.add_product(
                    product_identifier=product_id, quantity=quantity)

                if stock_info:
                    db.session.add(stock_info)
                else:
                    # This is an error message ( We only return 1 error at a time )
                    logs['Stock'] = message

        return logs
