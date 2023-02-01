import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from app.extensions import db
from app.utils import common
from app.utils.log import Log
from app.utils.result import Result


@dataclass
class Product(db.Model):
    # For serializing
    product_id: int
    product_name: str
    product_price: float

    product_id = db.Column(
        "product_id", db.Integer, primary_key=True, autoincrement=True
    )
    product_name = db.Column(db.String(20), unique=True, nullable=False)
    product_price = db.Column(db.DECIMAL(8, 2), nullable=False)
    machine_products = db.relationship("MachineStock", backref="product", lazy=True)

    # Aliases
    OptProduct = Optional["Product"]

    # Errors
    ERROR_NOT_FOUND = "Product Not Found"
    ERROR_CREATE_FAIL = "Product Creation Error"
    ERROR_EDIT_FAIL = "Product Edit Error"

    def __init__(self, name: str, price: float):  # noqa: ANN204
        self.product_name = name
        self.product_price = price

    @staticmethod
    def find_by_id(product_id: int) -> OptProduct:
        return db.session.get(Product, {"product_id": product_id})

    @staticmethod
    def find_by_name(
        name: str, first: bool = False
    ) -> Union[OptProduct, Optional[List["Product"]]]:

        exact_match = name == Product.product_name
        similar_match = Product.product_name.ilike(
            f"%{ name }%"
        )  # ilike is case insensitive

        found = Product.query.filter(exact_match or similar_match)

        if first:
            return found.first()

        return found.all()

    @staticmethod
    def find_by_name_or_id(
        identifier: (int | str), first: bool = False
    ) -> Union[OptProduct, Optional[List["Product"]]]:
        if common.isnumber(identifier):
            return Product.find_by_id(identifier)
        else:
            return Product.find_by_name(identifier, first)

    @staticmethod
    def make(name: str, price: float) -> Result:
        """Returns newly created product if succeeded, error otherwise.

        Args:
            name (str): Name of product.
            price (str): Price of product.

        Returns:
            Result: Newly created product and success/fail message.
        """
        if name is None:
            return Result.error("Product name is missing.")

        if price is None:
            return Result.error("Product price is missing.")

        if common.isnumber(name):
            return Result.error("The name cannot be a number.")

        try:
            casted_price = float(price)
            if casted_price < 0.0:
                return Result.error("Invalid price value. (price < 0.00)")

            if Product.find_by_name(name=name, first=True):
                return Result.error(
                    f"A product with the given name already exists. (Product Name: {name})"
                )

            return Result(
                Product(name=name, price=casted_price),
                f"Successfully added product: [{ name }, { casted_price }]",
            )

        except ValueError:
            return Result.error(
                f"The price value is invalid. (Incorrect type, expected float, got={type(price).__name__})"
            )

    # Returns the change log

    def _edit_name(self, new_name: str) -> Result:

        # Check redundancy
        if self.product_name == new_name:
            return Result.error("Name redundant, no changes made.")

        if common.isnumber(new_name):
            return Result.error("The name cannot be a number.")

        if Product.find_by_name(name=new_name, first=True):
            return Result.error(
                f"An existing product with the name '{new_name}' already exists."
            )

        log = f"Name: { self.product_name } -> { new_name }"
        self.product_name = new_name
        return Result.success(log)

    # Edits price and returns the change log
    def _edit_price(self, new_price: float) -> Result:

        # Note: The exception is handled here so it
        # can bubble the error message back to the log
        try:
            # Try casting
            _casted_new_price = float(new_price)
            casted_new_price = float(f"{_casted_new_price:.2f}")

            # Check redundancy
            if math.isclose(self.product_price, casted_new_price):
                return Result.error("Price redundant, no changes made.")

            log = f"Price: { self.product_price } -> { casted_new_price }"
            self.product_price = casted_new_price
            return Result.success(log)

        except ValueError:
            return Result.error(
                f"The price value is invalid. (Incorrect type, expected float, got={type(new_price).__name__})"
            )

    # Edits the product and returns the change log
    def edit(self, new_name: Optional[str], new_price: Optional[float]) -> Log:

        log = Log()

        if new_name is None and new_price is None:
            return log.error(Product.ERROR_EDIT_FAIL, "Nothing to edit.")

        if new_name:
            result = self._edit_name(new_name=new_name)
            log.add_result(
                "Product",
                f"Product ID {self.product_id}",
                result,
                Product.ERROR_EDIT_FAIL,
            )

        if new_price:
            result = self._edit_price(new_price=new_price)
            log.add_result(
                "Product",
                f"Product ID {self.product_id}",
                result,
                Product.ERROR_EDIT_FAIL,
            )

        return log

    # Returns a list of machines that the product can be found in
    # [ {id, loc, name}, ... ]
    def found_in(self) -> Optional[List[Dict[str, str]]]:

        if len(self.machine_products) == 0:
            return None

        machines: List[Dict[str, str]] = []

        for machine_stock in self.machine_products:
            machine = machine_stock.vending_machine
            entry = {
                "machine_id": machine.machine_id,
                "location": machine.location,
                "machine_name": machine.machine_name,
            }
            machines.append(entry)

        return machines
