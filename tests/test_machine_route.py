from typing import Any, Dict

import pytest

from app.models.vending_machine import Machine
from tests.fixtures.machine_tester import MachineTester
from tests.fixtures.product_tester import ProductTester


@pytest.fixture
def machine_tester(client):
    return MachineTester(client=client)


@pytest.fixture
def product_tester(client):
    return ProductTester(client=client)


@pytest.mark.parametrize(
    "machine_location, machine_name",
    [
        ("John Estate", "Rick"),
        ("Antarctica", "James"),
        ("Mars", "GSDE4A"),
        ("Atlantis", "John"),
    ],
)
def test_create_machine(machine_tester, machine_location, machine_name):
    _ = machine_tester.create_machine(machine_location, machine_name)
    assert machine_tester.no_error()


@pytest.mark.parametrize(
    "machine_location, machine_name, err_value",
    [
        ("123", "123", "Location can not be a number."),
        ("wow", 123.0, "Name can not be a number."),
        (12, "John", "Location can not be a number."),
        ("Location", 23, "Name can not be a number."),
    ],
)
def test_create_machine_fail(machine_tester, machine_location, machine_name, err_value):
    _ = machine_tester.create_machine(machine_location, machine_name)
    assert machine_tester.expect_error(
        expected_error=Machine.ERROR_CREATE_FAIL, value=err_value
    )


def test_get_machine(machine_tester):
    for machine_id in range(1, 11):
        _ = machine_tester.create_machine(f"location_{machine_id}", "some_name")
        assert machine_tester.no_error()

    # Make sure all can be found
    for search_machine_id in range(1, 11):
        _ = machine_tester.find_machine(
            location=f"location_{search_machine_id}", name="some_name"
        )
        assert machine_tester.no_error()

    # Add 3 machines to some_location_1
    for i in range(3):
        _ = machine_tester.create_machine("some_location_1", f"some_name_{i}")
        machine_tester.no_error()

    # Add 8 machines to some_location_6
    for i in range(8):
        _ = machine_tester.create_machine("some_location_6", f"some_name_{i}")
        machine_tester.no_error()

    # Make sure we get all 3 machines added to some_location_1
    search_response = machine_tester.find_machine("some_location_1")
    assert machine_tester.no_error() and len(search_response.json) == 3

    # Make sure we get all 8 machines added to some_location_1
    search_response = machine_tester.find_machine("some_location_6")
    assert machine_tester.no_error() and len(search_response.json) == 8


def test_get_machine_fail(machine_tester):
    _ = machine_tester.find_machine("some_location", "john")
    assert machine_tester.expect_error(
        expected_error=Machine.ERROR_NOT_FOUND,
        value="No machine found. (Location: some_location, Name: john)",
    )


def test_add_product_to_machine(machine_tester, product_tester):
    _ = product_tester.create_product(product_name="product_1", product_price=100.00)
    assert product_tester.no_error()

    _ = machine_tester.create_machine(location="some_location", name="some_name")
    assert machine_tester.no_error()

    _ = machine_tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )
    assert machine_tester.no_error() and machine_tester.log_has_entry(
        broad="Product", specific="Product ID 1"
    )

    _ = machine_tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )
    assert machine_tester.no_error()
    assert machine_tester.log_has_entry(broad="Product", specific="Product ID 1")


@pytest.mark.parametrize(
    "mid, json, expected, value",
    [
        (
            2,
            {"stock_list": [{"product_id": 1, "quantity": 10}]},
            Machine.ERROR_NOT_FOUND,
            None,
        ),
        (
            1,
            {"stock_list": [{"product_id": 1, "quantity": "string"}]},
            "Product ID 1",
            "Invalid quantity type. Expect int, got=str",
        ),
        (
            1,
            {"stock_list": [{"product_id": 1, "quantity": 123.4}]},
            "Product ID 1",
            "Invalid quantity type. Expect int, got=float",
        ),
        (1, {}, "JSON Error", None),
        (
            1,
            {"stock_list": [{"product_id": 1, "quantity": -10}]},
            "Product ID 1",
            "Quantity can not be negative. (got -10)",
        ),
    ],
)
def test_add_product_to_machine_fail(
    machine_tester,
    product_tester,
    mid: int,
    json: Dict[str, Any],
    expected: str,
    value: str,
):
    _ = product_tester.create_product(product_name="product_1", product_price=100.00)
    assert product_tester.no_error()

    _ = machine_tester.create_machine(location="some_location", name="some_name")
    assert machine_tester.no_error()

    _ = machine_tester.add_product_to_machine(machine_id=mid, json=json)
    assert machine_tester.expect_error(expected_error=expected, value=value)


def test_get_machine_by_id(machine_tester):
    machine_location = "some_location"
    machine_name = "some_name"
    machine_id = 1
    _ = machine_tester.create_machine(location=machine_location, name=machine_name)
    assert machine_tester.no_error()

    _ = machine_tester.get_machine_by_id(machine_id)
    assert machine_tester.no_error()

    assert machine_tester.response_has(
        location=machine_location, machine_name=machine_name, machine_id=machine_id
    )


@pytest.mark.parametrize("machine_id", [1, 2, 3, 4, 5])
def test_get_machine_by_id_error(machine_tester, machine_id):
    _ = machine_tester.get_machine_by_id(machine_id=machine_id)
    assert machine_tester.expect_error(
        expected_error=Machine.ERROR_NOT_FOUND,
        value=f"No machine with id {machine_id} found.",
    )


def test_edit_machine(machine_tester, product_tester):
    machine_location = "some_location"
    machine_name = "some_name"
    machine_id = 1

    # Add machine
    _ = machine_tester.create_machine(location=machine_location, name=machine_name)
    assert machine_tester.no_error() and machine_tester.log_has_entry(broad="Machine")

    _ = machine_tester.get_machine_by_id(machine_id)
    assert machine_tester.no_error()

    assert machine_tester.response_has(
        machine_name="some_name", location="some_location"
    )

    # Add product
    _ = product_tester.create_product(product_name="product_1", product_price=100.00)
    assert product_tester.no_error()

    _ = machine_tester.edit_machine(
        machine_id=machine_id,
        json={
            "machine_name": "new_name",
            "location": "new_location",
            "stock_list": [
                {"product_id": 1, "quantity": 100},
            ],
        },
    )
    assert machine_tester.no_error()

    _ = machine_tester.get_machine_by_id(machine_id)
    assert machine_tester.no_error()

    assert machine_tester.response_has(machine_name="new_name", location="new_location")

    assert len(machine_tester.prev_response.json.get("machine_products")) == 1


def test_edit_machine_error_not_found(machine_tester):
    # Machine not found
    _ = machine_tester.edit_machine(
        machine_id=123,
        json={
            "machine_name": "new_name",
            "location": "new_location",
            "stock_list": [
                {"product_id": 1, "quantity": 100},
            ],
        },
    )
    assert machine_tester.expect_error(
        expected_error=Machine.ERROR_NOT_FOUND, value="No machine with id 123 found."
    )


@pytest.mark.parametrize(
    "machine_id, json, expected_error, value",
    [
        (
            123,
            None,
            Machine.ERROR_NOT_FOUND,
            "No machine with id 123 found.",
        ),  # Machine not found
        (1, {}, "JSON Error", "Invalid JSON body."),  # Invalid JSON body
        (
            1,
            {"machine_name": "some_name"},
            Machine.ERROR_EDIT_FAIL,
            "Name redundant, no changes made.",
        ),
        # Name redundant
        (
            1,
            {"machine_name": 123},
            Machine.ERROR_EDIT_FAIL,
            "Name can not be numeric.",
        ),  # Name numeric
        (
            1,
            {"location": "some_location_2"},
            Machine.ERROR_EDIT_FAIL,
            "An existing machine with the name 'some_name' already exists at 'some_location_2'",
        ),
        # Clash with pre-existing machine
        (
            1,
            {"location": 123},
            Machine.ERROR_EDIT_FAIL,
            "Location can not be numeric.",
        ),  # Location numeric
        (
            1,
            {"location": "some_location"},
            Machine.ERROR_EDIT_FAIL,
            "Location redundant, no changes made.",
        ),
        # Location redundant
        (
            1,
            {"machine_name": None, "location": None, "stock_list": None},
            Machine.ERROR_EDIT_FAIL,
            "Nothing to edit.",
        ),
        # No edit info given
        (
            1,
            {"machine_name": "taken_name", "location": "taken_location"},
            Machine.ERROR_EDIT_FAIL,
            "An existing machine with the name 'taken_name' already exists at 'taken_location'",
        ),
        # Clash with existing machine at location
    ],
)
def test_edit_machine_error(
    machine_tester,
    machine_id: int,
    json: Dict[str, Any],
    expected_error: str,
    value: str,
):
    _ = machine_tester.create_machine(location="some_location", name="some_name")
    _ = machine_tester.create_machine(location="some_location_2", name="some_name")
    _ = machine_tester.create_machine(location="taken_location", name="taken_name")
    assert machine_tester.no_error()

    _ = machine_tester.edit_machine(machine_id=machine_id, json=json)
    assert machine_tester.expect_error(expected_error=expected_error, value=value)


def test_get_all_machines(machine_tester):
    for i in range(5):
        _ = machine_tester.create_machine(
            location="some_location", name=f"some_name_{i}"
        )
    _ = machine_tester.get_all_machines()
    assert machine_tester.no_error() and len(machine_tester.prev_response.json) == 5


def test_get_all_machines_error_missing(machine_tester):
    _ = machine_tester.get_all_machines()
    assert machine_tester.expect_error(
        expected_error=Machine.ERROR_NOT_FOUND, value="There are no existing machines"
    )


@pytest.mark.parametrize("payment", [100.00, 120.00, 1000])
def test_buy_product_from_machine(machine_tester, product_tester, payment: int):
    _ = product_tester.create_product(product_name="product_1", product_price=100.00)
    assert product_tester.no_error()

    _ = machine_tester.create_machine(location="some_location", name="some_name")
    assert machine_tester.no_error()

    _ = machine_tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )
    assert machine_tester.no_error()

    _ = machine_tester.buy_product_from_machine(
        machine_id=1, product_id=1, json={"payment": payment}
    )
    assert machine_tester.no_error()

    # Check payment success
    assert machine_tester.log_has_entry(
        broad="Transaction", specific="Success", value="Successfully bought product."
    )

    # Check correct change
    assert machine_tester.log_has_entry(
        broad="Transaction", specific="Change", value=str(float(payment) - 100.0)
    )


@pytest.mark.parametrize(
    "mid, pid, payment_json, expected_error, value",
    [
        (1, 1, {}, "JSON Error", "Invalid JSON body."),  # Invalid JSON
        (
            2,
            1,
            {"payment": 100},
            Machine.ERROR_NOT_FOUND,
            "No machine with id 2 found.",
        ),  # Machine not found
        (
            1,
            1,
            {"payment": None},
            Machine.ERROR_PURCHASE_FAIL,
            "No payment received.",
        ),  # No payment given
        (
            1,
            1,
            {"payment": "foo"},
            Machine.ERROR_PURCHASE_FAIL,
            "Invalid payment type.",
        ),  # Invalid payment
        (
            1,
            2,
            {"payment": 100},
            Machine.ERROR_PURCHASE_FAIL,
            "Product is out of stock.",
        ),  # Out of stock
        (
            1,
            1,
            {"payment": 50},
            Machine.ERROR_PURCHASE_FAIL,
            "Not enough money, costs 100.0 Baht, got 50.0 Baht.",
        ),
        (
            1,
            3,
            {"payment": 100},
            Machine.ERROR_PURCHASE_FAIL,
            "Product is not in stock.",
        ),
    ],
)
def test_buy_product_from_machine_error(
    machine_tester,
    product_tester,
    mid: int,
    pid: int,
    payment_json: Dict[str, Any],
    expected_error: str,
    value: str,
):
    # Product 1
    _ = product_tester.create_product(product_name="product_1", product_price=100.00)
    assert product_tester.no_error()

    # Product 2
    _ = product_tester.create_product(product_name="product_2", product_price=100.00)
    assert product_tester.no_error()

    # Machine 1
    _ = machine_tester.create_machine(location="some_location", name="some_name")
    assert machine_tester.no_error()

    # Add product 1 (qt=10) to machine 1
    _ = machine_tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )
    assert machine_tester.no_error()

    # Add product 2 (qt=1) to machine 1
    _ = machine_tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 2, "quantity": 1}]}
    )
    assert machine_tester.no_error()

    # Buy product 2 (qt=1) from machine 1
    _ = machine_tester.buy_product_from_machine(
        machine_id=1, product_id=2, json={"payment": 100}
    )
    assert machine_tester.no_error()

    # Buy test
    _ = machine_tester.buy_product_from_machine(
        machine_id=mid, product_id=pid, json=payment_json
    )
    assert machine_tester.expect_error(expected_error=expected_error, value=value)


def test_remove_product_from_machine(machine_tester, product_tester):
    _ = product_tester.create_product(product_name="product_1", product_price=100.00)
    assert product_tester.no_error()

    _ = machine_tester.create_machine(location="some_location", name="some_name")
    assert machine_tester.no_error()

    _ = machine_tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )
    assert machine_tester.no_error()

    _ = machine_tester.remove_product_from_machine(machine_id=1, product_id=1)

    assert machine_tester.no_error() and machine_tester.log_has_entry(
        broad="Machine", specific="Machine ID 1"
    )


@pytest.mark.parametrize(
    "mid, pid, expected_error",
    [(1, 2, Machine.ERROR_REMOVE_PRODUCT), (2, 1, Machine.ERROR_NOT_FOUND)],
)
def test_remove_product_from_machine_fail(
    machine_tester, product_tester, mid: int, pid: int, expected_error: str
):
    _ = product_tester.create_product(product_name="product_1", product_price=100.00)
    assert product_tester.no_error()

    _ = machine_tester.create_machine(location="some_location", name="some_name")
    assert machine_tester.no_error()

    _ = machine_tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )
    assert machine_tester.no_error()

    _ = machine_tester.remove_product_from_machine(machine_id=mid, product_id=pid)

    assert machine_tester.expect_error(expected_error=expected_error)


@pytest.mark.parametrize("machines_count", [1, 2, 3, 120])
def test_remove_machine(machine_tester, machines_count: int):
    for machine_id in range(machines_count):
        _ = machine_tester.create_machine(
            location="some_location", name=f"some_name_{machine_id}"
        )
        assert machine_tester.no_error()

    for machine_id in range(machines_count):
        _ = machine_tester.remove_machine(machine_id=(machine_id + 1))
        assert machine_tester.no_error()


def test_remove_machine_error(machine_tester):
    _ = machine_tester.remove_machine(machine_id=42)
    assert machine_tester.expect_error(expected_error=Machine.ERROR_NOT_FOUND)


def test_get_product_time_stamp_from_records(machine_tester, product_tester):
    _ = product_tester.create_product(product_name="product_1", product_price=100.00)
    assert product_tester.no_error()

    _ = machine_tester.create_machine(location="some_location", name="some_name")
    assert machine_tester.no_error()

    _ = machine_tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )
    assert machine_tester.no_error()

    _ = machine_tester.get_product_time_stamp_from_records(1)
    assert machine_tester.no_error()
    assert machine_tester.response_has(machine_id=1, product_id=1, quantity=10)
    assert len(machine_tester.prev_response.json) == 1


def test_get_product_time_stamp_from_records_error(machine_tester):
    from app.models.vending_machine_record import StockRecord

    _ = machine_tester.get_product_time_stamp_from_records(1)
    assert machine_tester.expect_error(
        expected_error=StockRecord.ERROR_NOT_FOUND, value="Product not found"
    )


def test_get_machine_time_stamp_from_records(machine_tester, product_tester):
    _ = product_tester.create_product(product_name="product_1", product_price=100.00)
    assert product_tester.no_error()

    _ = product_tester.create_product(product_name="product_2", product_price=100.00)
    assert product_tester.no_error()

    _ = machine_tester.create_machine(location="some_location", name="some_name")
    assert machine_tester.no_error()

    _ = machine_tester.add_product_to_machine(
        machine_id=1,
        json={
            "stock_list": [
                {"product_id": 1, "quantity": 100},
                {"product_id": 2, "quantity": 10},
            ]
        },
    )
    assert machine_tester.no_error()

    _ = machine_tester.get_machine_time_stamp_from_records(1)
    assert machine_tester.no_error()
    assert machine_tester.response_has(machine_id=1, product_id=1, quantity=100)
    assert len(machine_tester.prev_response.json) == 2


def test_get_machine_time_stamp_from_records_error(machine_tester):
    from app.models.vending_machine_record import StockRecord

    _ = machine_tester.get_machine_time_stamp_from_records(1)
    assert machine_tester.expect_error(
        expected_error=StockRecord.ERROR_NOT_FOUND, value="Machine not found"
    )
