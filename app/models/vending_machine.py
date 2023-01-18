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
    balance: float

    machine_id = db.Column('machine_id', db.Integer,
                           primary_key=True, autoincrement=True)
    machine_name = db.Column(db.String(20), unique=False, nullable=False)
    location = db.Column(db.String(20), unique=False, nullable=False)
    products = db.relationship(
        "MachineStock", backref="vending_machine", lazy=True)
    balance = db.Column(db.DECIMAL(20, 2), nullable=False, default=0.0)

    # Aliases
    ListOfMachines = List["Machine"]
    OptMachine = Optional["Machine"]

    @staticmethod
    def make(location: str, name: str, products: Optional[MachineStock.ListOfStockInfo] = None) -> Tuple[OptMachine, str]:

        if name.isnumeric():
            return None, "Name can not be numeric."

        if location.isnumeric():
            return None, "Location can not be numeric."

        if Machine.find(name=name, location=location):
            return None, f"A machine with given name and location already exists. (Location: { location }, Name: { name })"

        new_machine = Machine(location=location, machine_name=name)

        if products:
            for product in products:
                stock, message = new_machine.add_product(product.product_id)

                if stock is None:
                    return None, message

        return new_machine, f"Successfully added vending machine named '{name}' at '{ location }'!"

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

    def add_product(self, product_id: (int | str), quantity: int) -> Tuple[MachineStock.OptStock, str]:
        
        if stock := MachineStock.get(machine_id=self.machine_id,product_id=product_id):
            old_quantity = stock.quantity
            stock.quantity += quantity
            return None, f"Updated stock: {old_quantity} -> {stock.quantity}"
        
        return MachineStock.make(machine_id=self.machine_id, product_id=product_id, quantity=quantity)

    # Returns the change log
    def _edit_name(self, new_name: str) -> str:

        # Check redundancy
        if self.machine_name == new_name:
            return "Failed, name redundant, no changes made."
        
        if new_name.isnumeric():
            return "Failed, name can not be numeric."

        if Machine.find( name=new_name, location=self.location ):
            return f"Failed, an existing machine with the name '{new_name}' already exists at '{self.location}'"

        log = f'{ self.machine_name } -> { new_name }'
        self.machine_name = new_name
        return log

    # Returns the change log
    def _edit_location(self, new_location: str):

        # Check redundancy
        if self.location == new_location:
            return "Failed, location redundant, no changes made"

        if new_location.isnumeric():
            return "Failed, location can not be numeric."

        if Machine.find( name=self.machine_name, location=new_location ):
            return f"Failed, an existing machine with the name '{self.machine_name}' already exists at '{new_location}'"

        log = f'{ self.location } -> { new_location }'
        self.location = new_location
        return log

    # Edits the machine and returns the change log
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

        if new_location:
            location_log = self._edit_location(new_location=new_location)
            logs['Location'] = location_log

        if new_name:
            name_log = self._edit_name(new_name=new_name)
            logs['Name'] = name_log

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
                    product_id=product_id, quantity=quantity)

                if stock_info:
                    db.session.add(stock_info)
                else:
                    # This is an error message ( We only return 1 error at a time )
                    # Notice that this DOES NOT throw any exception, but it does
                    # signal that something has gone wrong (though not fatal)
                    logs['Stock'] = message

        return logs


    # Returns ( Change, Message )
    def buy_product(self, product_id: int, payment: float) -> Tuple[ float, str ]: 
        
        casted_payment: float
        try:
            casted_payment = float(payment)
        except ValueError:
            return payment, "Invalid payment type."

        if product_stock := MachineStock.get(self.machine_id, product_id):
            
            if product_stock.out_of_stock():
                return casted_payment, "Product is out of stock."

            if (price := product_stock.product.product_price) > casted_payment:
                return casted_payment, f"Not enough money, costs {price} Baht, got {casted_payment} Baht."
            else:
                product_stock.decrease_stock()
                self.balance = float(self.balance) + float(price)
                db.session.commit()
                return casted_payment-float(price), "Successfully bought product."

        # Product not found, product out of stock
        return payment, "Product is not in stock."

    
    def remove_stock(self, product_id: id) -> str:
        
        if stock := MachineStock.get(machine_id=self.machine_id, product_id=product_id):
            stock.remove_from_machine()
            return "Successfully removed product from machine."
        
        return "Product not found in machine."