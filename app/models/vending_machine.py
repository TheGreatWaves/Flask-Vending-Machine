from dataclasses import dataclass
from typing import List, Optional, Union

import sqlalchemy

from app.extensions import db
from app.models.vending_machine_stock import MachineStock
from app.utils import common
from app.utils.log import Log
from app.utils.result import Result


@dataclass
class Machine(db.Model):
    # For serializing
    machine_id: int
    machine_name: str
    location: str
    products: sqlalchemy.orm.Mapped[List[MachineStock]]
    balance: float

    machine_id = db.Column(
        "machine_id", db.Integer, primary_key=True, autoincrement=True
    )
    machine_name = db.Column(db.String(20), unique=False, nullable=False)
    location = db.Column(db.String(20), unique=False, nullable=False)
    products = db.relationship("MachineStock", backref="vending_machine", lazy=True)
    balance = db.Column(db.DECIMAL(20, 2), nullable=False, default=0.0)

    # Aliases
    ListOfMachines = List["Machine"]
    OptMachine = Optional["Machine"]

    # Defining/ Classifying errors
    ERROR = "Machine Error"
    ERROR_NOT_FOUND = "Machine Not Found"
    ERROR_CREATE_FAIL = "Machine Creation Error"
    ERROR_REMOVE_PRODUCT = "Machine Product Removal Error"

    @staticmethod
    def make(location: str, name: str) -> Result:

        if common.isnumber(location):
            return Result.error("Location can not be a number.")

        if common.isnumber(name):
            return Result.error("Name can not be a number.")

        if Machine.find(name=name, location=location):
            return Result.error(
                f"A machine with given name and location already exists. (Location: {location}, Name: {name})"
            )

        new_machine = Machine(location=location, machine_name=name)

        return Result(
            new_machine,
            f"Successfully added vending machine named '{name}' at '{location}'!",
        )

    @staticmethod
    def find_by_id(id: int) -> Result:
        if machine := Machine.query.get(id):
            return Result(machine)
        return Result.error(f"No machine with id {id} found.")

    @staticmethod
    def __find_by_name(name: str):  # noqa: ANN205
        return Machine.query.filter_by(machine_name=name)

    @staticmethod
    def find_by_name(name: str) -> OptMachine:
        return Machine.__find_by_name(name=name).first()

    @staticmethod
    def __find_by_location(location: str):  # noqa: ANN205
        exact_match = Machine.location == location
        similar_match = Machine.location.ilike(
            f"%{location}%"
        )  # ilike is case insensitive

        return Machine.query.filter(exact_match or similar_match)

    @staticmethod
    def find_by_location(location: str) -> Optional[ListOfMachines]:
        return Machine.__find_by_location(location=location).all()

    @staticmethod
    def find(
            name: Optional[str] = None, location: Optional[str] = None
    ) -> Union[OptMachine, Optional[ListOfMachines]]:

        # Nothing given
        if name is None and location is None:
            return None

        # Only name given
        if name and location:
            return (
                Machine.__find_by_location(location=location)
                .filter_by(machine_name=name)
                .first()
            )

        if location:
            return Machine.find_by_location(location=location)

        if name:
            return Machine.find_by_name(name=name)

    def add_product(self, product_id: (int | str), quantity: int) -> Result:

        if not isinstance(quantity, int):
            return Result.error(
                f"Invalid quantity type. Expect int, got={type(quantity).__name__}"
            )

        if quantity < 0:
            return Result.error(f"Quantity can not be negative. (got {quantity})")

        if stock := MachineStock.get(machine_id=self.machine_id, product_id=product_id):
            old_quantity = stock.quantity
            stock.quantity += quantity
            return Result(stock, f"Updated stock: {old_quantity} -> {stock.quantity}")

        return MachineStock.make(
            machine_id=self.machine_id, product_id=product_id, quantity=quantity
        )

    # Returns the change log
    def _edit_name(self, new_name: str) -> Result:

        # Check redundancy
        if self.machine_name == new_name:
            return Result.error("Name redundant, no changes made.")

        if common.isnumber(new_name):
            return Result.error("Name can not be numeric.")

        if Machine.find(name=new_name, location=self.location):
            return Result.error(
                f"An existing machine with the name '{new_name}' already exists at '{self.location}'"
            )

        log = f"{self.machine_name} -> {new_name}"
        self.machine_name = new_name
        return Result.success(log)

    # Returns the change log
    def _edit_location(self, new_location: str) -> Result:

        # Check redundancy
        if self.location == new_location:
            return Result.error("Location redundant, no changes made")

        if common.isnumber(new_location):
            return Result.error("Location can not be numeric.")

        if Machine.find(name=self.machine_name, location=new_location):
            return Result.error(
                f"An existing machine with the name '{self.machine_name}' already exists at '{new_location}'"
            )

        log = f"{self.location} -> {new_location}"
        self.location = new_location
        return Result.success(log)

    # Edits the machine and returns the change log
    def edit(
            self,
            new_name: Optional[str],
            new_location: Optional[str],
            new_stock: Optional[MachineStock.ListOfStockInfo],
    ) -> Log:

        log = Log()

        if new_name is None and new_location is None and new_stock is None:
            return Log().error("Edit Error", "Nothing to edit")

        machine_info = f"Machine ID {self.machine_id}"

        if new_location:
            result = self._edit_location(new_location=new_location)
            log.add_result("Edit", machine_info, result)

        if new_name:
            result = self._edit_name(new_name=new_name)
            log.add_result("Edit", machine_info, result)

        if new_stock:
            # Delete current stock
            self.remove_all_stock()

        product_log = self.add_products(new_stock)
        log += product_log

        return log

    def add_products(self, stocks: Optional[MachineStock.ListOfStockInfo]) -> Log:
        if stocks is None:
            return Log().error("Product Error", "No product(s) provided.")

        log = Log()

        # Add all new stock
        for product_id, quantity in stocks:
            stock_info, message = self.add_product(
                product_id=product_id, quantity=quantity
            )

            if stock_info:
                log.add("Product", f"Product ID {product_id}", message)
                if stock_info.product is None:
                    db.session.add(stock_info)
            else:
                log.error(f"Product ID {product_id}", message)

        return log

    def remove_all_stock(self) -> None:
        delete_stock = MachineStock.__table__.delete().where(
            MachineStock.machine_id == self.machine_id
        )
        db.session.execute(delete_stock)

    # Returns ( Change, Message )
    def buy_product(self, product_id: int, payment: float) -> Result:

        if payment is None:
            return Result.error("No payment received.")

        casted_payment: float
        try:
            # Ideally we should never get an
            # invalid json value type but just incase
            casted_payment = float(payment)

        except ValueError:
            return Result(payment, "Invalid payment type.")

        if product_stock := MachineStock.get(self.machine_id, product_id):

            if product_stock.out_of_stock():
                return Result(casted_payment, "Product is out of stock.")

            if (price := product_stock.product.product_price) > casted_payment:
                return Result(
                    casted_payment,
                    f"Not enough money, costs {price} Baht, got {casted_payment} Baht.",
                )
            else:
                product_stock.decrease_stock()
                self.balance = float(self.balance) + float(price)
                db.session.commit()
                return Result(
                    casted_payment - float(price), "Successfully bought product."
                )

        # Product not found, product out of stock
        return Result(payment, "Product is not in stock.")

    def remove_stock(self, product_id: id) -> Result:
        if stock := MachineStock.get(machine_id=self.machine_id, product_id=product_id):
            stock.remove_from_machine()
            return Result.success(
                f"Successfully removed product from machine. (Product ID: {product_id})"
            )
        return Result.error(
            f"Product not found in machine. (Machine ID: {self.machine_id}, Product ID: {product_id})"
        )

    def destroy(self) -> str:
        self.remove_all_stock()
        db.session.delete(self)
        return "Successfully deleted."
