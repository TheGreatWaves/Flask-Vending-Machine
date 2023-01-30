from typing import Dict, List, Optional

import pytest

from app.extensions import db
from app.models.product import Product
from app.models.vending_machine import Machine
from app.models.vending_machine_stock import MachineStock


def test_make(app):
    with app.app_context():
        db.session.add(Machine.make(location="some_place", name="john").object)
        db.session.add(Product.make(name="Candy", price=100.0).object)
        db.session.commit()

        success, msg = MachineStock.make(machine_id=1, product_id=1, quantity=10)

        assert success and msg == "Added product 1 to machine 1 successfully. (qt=10)"


@pytest.mark.parametrize(
    "mid, pid, qt, expected_err",
    [
        (2, 1, 10, "No machine with id 2 found."),
        (1, 2, 10, "No product with ID 2 found."),
        (2.1, 1, 10, "Invalid machine ID type. Expected int, got=float"),
        (1, 1.2, 10, "Invalid product ID type. Expected int, got=float"),
        (1, 1, -10, "Invalid quantity. (-10 <= 0)"),
    ],
)
def test_make_fail(app, mid: int, pid: int, qt: int, expected_err: str):
    with app.app_context():
        db.session.add(Machine.make(location="some_place", name="john").object)
        db.session.add(Product.make(name="Candy", price=100.0).object)
        db.session.commit()

        success, err = MachineStock.make(machine_id=mid, product_id=pid, quantity=qt)

        assert success is None and err == expected_err


def test_make_duplicate(app):
    with app.app_context():
        db.session.add(Machine.make(location="some_place", name="john").object)
        db.session.add(Product.make(name="Candy", price=100.0).object)
        db.session.commit()

        obj, _ = MachineStock.make(machine_id=1, product_id=1, quantity=1)

        db.session.add(obj)
        db.session.commit()

        success, err = MachineStock.make(machine_id=1, product_id=1, quantity=1)

        assert (
            success is None
            and err == "An existing entry already exists for machine 1 and product 1"
        )


@pytest.mark.parametrize(
    "raw, expected",
    [
        (None, None),
        ({"message": "Hi"}, None),
        ("John!?", None),
        ([{"product_id": 1, "quantity": 10}], [(1, 10)]),
        (
            [{"product_id": 1, "quantity": 10}, {"product_id": 2, "quantity": 200}],
            [(1, 10), (2, 200)],
        ),
        (["My name is John"], None),
    ],
)
def test_process_raw(
    raw: Optional[List[Dict[str, str]]],
    expected: Optional[MachineStock.ListOfStockInfo],
):
    assert MachineStock.process_raw(raw=raw) == expected


@pytest.mark.parametrize("amount", [1, 2, 6, 1000])
def test_add_stock(app, amount: int):
    with app.app_context():
        db.session.add(Machine.make(location="some_place", name="john").object)
        db.session.add(Product.make(name="Candy", price=100.0).object)
        db.session.commit()

        db.session.add(
            MachineStock.make(machine_id=1, product_id=1, quantity=10).object
        )
        db.session.commit()

        stock = MachineStock.get(machine_id=1, product_id=1)

        for _ in range(amount):
            stock.add_stock()

        assert stock.quantity == (10 + amount)
