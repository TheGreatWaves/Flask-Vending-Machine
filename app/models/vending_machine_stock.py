from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, TypeAlias

from app.extensions import db
from app.models import product, vending_machine
from app.utils.result import Result

"""
This represents the relationship between
the machines and the products they have.
"""


@dataclass
class MachineStock(db.Model):
    # For serializing
    product_id: int
    product_name: str
    product_price: float
    quantity: int

    machine_id = db.Column(
        db.Integer, db.ForeignKey("machine.machine_id"), primary_key=True
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey("product.product_id"), primary_key=True
    )
    quantity = db.Column(db.Integer, nullable=False)

    # Aliases
    ProductQuantity: TypeAlias = int
    ProductID: TypeAlias = int
    OptStock: TypeAlias = Optional["MachineStock"]
    StockInfo: TypeAlias = Tuple[ProductID, ProductQuantity]
    ListOfStockInfo: TypeAlias = List[StockInfo]

    @staticmethod
    def get(machine_id: int, product_id: int) -> OptStock:
        return MachineStock.query.filter_by(
            machine_id=machine_id, product_id=product_id
        ).first()

    @staticmethod
    def make(machine_id: int, product_id: int, quantity: int) -> Result:

        target_machine, machine_not_found_msg = vending_machine.Machine.find_by_id(
            machine_id
        )
        if target_machine is None:
            return Result.error(machine_not_found_msg)

        if not isinstance(product_id, int):
            return Result.error(
                f"Invalid product ID type. Expected int, got={type(product_id).__name__}"
            )

        target_product = product.Product.find_by_name_or_id(
            identifier=product_id, first=True
        )
        if target_product is None:
            return Result.error(f"No product with ID { product_id } found.")

        if quantity <= 0:
            return Result.error(f"Invalid quantity. ({quantity} <= 0)")

        # Prevent duplicate entry
        if MachineStock.get(
            machine_id=machine_id,
            product_id=product_id,
        ):
            return Result.error(
                f"An existing entry already exists for machine { machine_id } and product { target_product.product_id }"
            )

        return Result(
            MachineStock(
                machine_id=machine_id,
                product_id=target_product.product_id,
                quantity=quantity,
            ),
            f"Added product { target_product.product_id } to machine { machine_id } successfully. (qt={quantity})",
        )

    @property
    def product_name(self) -> str:
        return self.product.product_name

    @property
    def product_price(self) -> float:
        return self.product.product_price

    """
    Processes the following json body into a list of tuples ( pid, quantity )

    [
        {
            "product_id": <product_id>,
            "quantity": <quantity>
        },
        ...
    ]
    """

    @staticmethod
    def process_raw(raw: Optional[List[Dict[str, str]]]) -> Optional[ListOfStockInfo]:

        if raw is None or not isinstance(raw, List):
            return None

        stock_information_list: MachineStock.ListOfStockInfo = []

        for stock_info in raw:

            if not isinstance(stock_info, Dict):
                return None

            product_id = stock_info.get("product_id")
            quantity = stock_info.get("quantity")
            stock_information_list.append((product_id, quantity))

        return stock_information_list

    def remove_from_machine(self) -> None:
        db.session.delete(self)

    def decrease_stock(self) -> None:
        self.quantity -= 1

    def add_stock(self) -> None:
        self.quantity += 1

    def out_of_stock(self) -> bool:
        return self.quantity == 0
