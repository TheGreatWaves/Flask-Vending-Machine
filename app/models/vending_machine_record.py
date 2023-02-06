from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.extensions import db


@dataclass
class StockRecord(db.Model):
    product_id: int
    machine_id: int
    time_stamp: datetime
    quantity: int

    machine_id = db.Column(
        db.Integer, db.ForeignKey("machine.machine_id"), primary_key=True
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey("product.product_id"), primary_key=True
    )
    time_stamp = db.Column(db.DateTime, primary_key=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    ERROR_NOT_FOUND = "Record not found"

    @staticmethod
    def make(product_id: int, machine_id: int) -> None:
        from app.models.vending_machine_stock import MachineStock

        stock = db.session.get(
            MachineStock, {"product_id": product_id, "machine_id": machine_id}
        )

        if stock:
            quantity = stock.quantity

            record = StockRecord(
                product_id=product_id,
                machine_id=machine_id,
                time_stamp=datetime.now(),
                quantity=quantity,
            )
            db.session.add(record)
            db.session.commit()

    @staticmethod
    def product_time_stamp_in_records(product_id: int) -> Optional[List["StockRecord"]]:
        stock_record = StockRecord.query.filter_by(product_id=product_id).all()
        return stock_record

    @staticmethod
    def machine_time_stamp_in_records(machine_id: int) -> Optional[List["StockRecord"]]:
        stock_record = StockRecord.query.filter_by(machine_id=machine_id).all()
        return stock_record


def take_snapshot(func):  # noqa: ANN001, ANN201
    def wrapper(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN201
        result = func(self, *args, **kwargs)

        product_id = kwargs.get("product_id")
        if product_id is None:
            product_id = self.product_id

        StockRecord.make(product_id=product_id, machine_id=self.machine_id)

        return result

    return wrapper
