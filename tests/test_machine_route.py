from typing import Any, Dict, Optional

import pytest
from werkzeug.test import TestResponse

from app.models.vending_machine import Machine
from app.utils.log import Log
from tests.conftest import Tester, save_response


@pytest.fixture
def tester(client):
    return MachineTest(client=client)


class MachineTest(Tester):
    @save_response
    def create_machine(self, location: str, name: str) -> TestResponse:
        return self.client.post(f"/machine/create/{location}/{name}")

    @save_response
    def find_machine(self, location: str, name: Optional[str] = None) -> TestResponse:
        if name:
            return self.client.get(f"/machine/at/{location}/{name}")
        return self.client.get(f"/machine/at/{location}")

    @save_response
    def add_product_to_machine(
        self, machine_id: int, json: Dict[str, Any]
    ) -> TestResponse:
        return self.client.post(f"/machine/{machine_id}/add", json=json)

    @save_response
    def get_machine_by_id(self, machine_id: int) -> TestResponse:
        return self.client.get(f"/machine/{machine_id}")

    @save_response
    def edit_machine(self, machine_id: int, json: Dict[str, Any]) -> TestResponse:
        return self.client.post(f"/machine/{machine_id}/edit", json=json)

    @save_response
    def get_all_machines(self) -> TestResponse:
        return self.client.get("/machine/all")

    @save_response
    def buy_product_from_machine(
        self, machine_id: int, product_id: int, json: Dict[str, Any]
    ):
        return self.client.post(f"/machine/{machine_id}/buy/{product_id}", json=json)

    @save_response
    def remove_product_from_machine(self, machine_id: int, product_id: int):
        return self.client.post(f"/machine/{machine_id}/remove/{product_id}")

    @save_response
    def remove_machine(self, machine_id: int):
        return self.client.post(f"/machine/{machine_id}/destroy")


@pytest.mark.parametrize(
    "machine_location, machine_name",
    [
        ("John Estate", "Rick"),
        ("Antarctica", "James"),
        ("Mars", "GSDE4A"),
        ("Atlantis", "John"),
    ],
)
def test_create_machine(tester, machine_location, machine_name):
    _ = tester.create_machine(machine_location, machine_name)
    assert tester.no_error()


@pytest.mark.parametrize(
    "machine_location, machine_name",
    [("123", "123"), ("wow", 123.0), (12, "John"), ("Location", 23)],
)
def test_create_machine_fail(tester, machine_location, machine_name):
    create_response = tester.create_machine(machine_location, machine_name)
    assert MachineTest.expect_error_from_response(
        create_response, Machine.ERROR_CREATE_FAIL
    )


def test_get_machine(tester):
    for machine_id in range(1, 11):
        _ = tester.create_machine(f"location_{machine_id}", "some_name")

    # Make sure all can be found
    for search_machine_id in range(1, 11):
        search_response = tester.find_machine(
            f"location_{search_machine_id}", "some_name"
        )
        assert tester.no_error()

    # Add 3 machines to some_location_1
    for i in range(3):
        _ = tester.create_machine("some_location_1", f"some_name_{i}")

    # Add 8 machines to some_location_6
    for i in range(8):
        _ = tester.create_machine("some_location_6", f"some_name_{i}")

    # Make sure we get all 3 machines added to some_location_1
    search_response = tester.find_machine("some_location_1")
    assert tester.no_error() and len(search_response.json) == 3

    # Make sure we get all 8 machines added to some_location_1
    search_response = tester.find_machine("some_location_6")
    assert tester.no_error() and len(search_response.json) == 8


def test_get_machine_fail(tester):
    search_response = tester.find_machine("some_location", "john")
    assert MachineTest.expect_error_from_response(
        search_response, Machine.ERROR_NOT_FOUND
    )


def test_add_product_to_machine(tester, client):
    _ = client.post(
        "/product/create",
        json={"product_name": "product_1", "product_price": 100.00},
    )
    _ = tester.create_machine(location="some_location", name="some_name")
    add_response = tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )
    assert tester.no_error() and Log.make_from_response(
        response=add_response
    ).has_entry(broad="Product", specific="Product ID 1")

    add_more_response = tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )

    assert tester.no_error() and Log.make_from_response(
        response=add_more_response
    ).has_entry(broad="Product", specific="Product ID 1")


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
    tester, client, mid: int, json: Dict[str, Any], expected: str, value: str
):
    _ = client.post(
        "/product/create",
        json={"product_name": "product_1", "product_price": 100.00},
    )
    _ = tester.create_machine(location="some_location", name="some_name")

    add_response = tester.add_product_to_machine(machine_id=mid, json=json)
    assert MachineTest.expect_error_from_response(
        response=add_response, expected_error=expected, value=value
    )


def test_get_machine_by_id(tester):
    machine_location = "some_location"
    machine_name = "some_name"
    machine_id = 1
    _ = tester.create_machine(location=machine_location, name=machine_name)

    get_response = tester.get_machine_by_id(machine_id)
    assert (
        tester.no_error()
        and get_response.json.get("location") == machine_location
        and get_response.json.get("machine_name") == machine_name
        and get_response.json.get("machine_id") == machine_id
    )


@pytest.mark.parametrize("machine_id", [1, 2, 3, 4, 5])
def test_get_machine_by_id_error(tester, machine_id):
    get_response = tester.get_machine_by_id(machine_id=machine_id)
    assert MachineTest.expect_error_from_response(get_response, Machine.ERROR_NOT_FOUND)


def test_edit_machine(tester, client):
    machine_location = "some_location"
    machine_name = "some_name"
    machine_id = 1

    # Add machine
    create_response = tester.create_machine(
        location=machine_location, name=machine_name
    )

    assert tester.no_error() and Log.make_from_response(
        response=create_response
    ).has_entry(broad="Machine")

    get_response = tester.get_machine_by_id(machine_id)
    print(get_response.json)
    assert (
        tester.no_error()
        and get_response.json.get("machine_name") == "some_name"
        and get_response.json.get("location") == "some_location"
    )

    # Add product
    _ = client.post(
        "/product/create",
        json={"product_name": "product_1", "product_price": 100.00},
    )

    _ = tester.edit_machine(
        machine_id=machine_id,
        json={
            "machine_name": "new_name",
            "location": "new_location",
            "stock_list": [
                {"product_id": 1, "quantity": 100},
            ],
        },
    )

    assert tester.no_error()
    get_updated_response = tester.get_machine_by_id(machine_id)

    assert (
        tester.no_error()
        and get_updated_response.json.get("machine_name") == "new_name"
        and get_updated_response.json.get("location") == "new_location"
        and len(get_updated_response.json.get("machine_products")) == 1
    )


def test_edit_machine_error_not_found(tester):
    # Machine not found
    edit_response = tester.edit_machine(
        machine_id=123,
        json={
            "machine_name": "new_name",
            "location": "new_location",
            "stock_list": [
                {"product_id": 1, "quantity": 100},
            ],
        },
    )

    assert MachineTest.expect_error_from_response(
        edit_response, Machine.ERROR_NOT_FOUND
    )


def test_edit_machine_error_invalid_json(tester):
    # Invalid json
    _ = tester.create_machine(location="some_location", name="some_name")

    edit_response = tester.edit_machine(machine_id=1, json={})

    assert MachineTest.expect_error_from_response(edit_response, "JSON Error")


def test_get_all_machines(tester):
    for i in range(5):
        _ = tester.create_machine(location="some_location", name=f"some_name_{i}")
    get_all_response = tester.get_all_machines()
    assert tester.no_error() and len(get_all_response.json) == 5


def test_get_all_machines_error_missing(tester):
    get_all_response = tester.get_all_machines()
    assert MachineTest.expect_error_from_response(
        response=get_all_response, expected_error=Machine.ERROR_NOT_FOUND
    )


@pytest.mark.parametrize("payment", [100.00, 120.00, 1000])
def test_buy_product_from_machine(tester, client, payment: int):
    _ = client.post(
        "/product/create",
        json={"product_name": "product_1", "product_price": 100.00},
    )
    _ = tester.create_machine(location="some_location", name="some_name")

    _ = tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )

    buy_product_response = tester.buy_product_from_machine(
        machine_id=1, product_id=1, json={"payment": payment}
    )

    assert tester.no_error() and buy_product_response.json.get("Change") == (
        payment - 100.00
    )


@pytest.mark.parametrize(
    "mid, pid, payment_json, expected_error",
    [(1, 1, {}, "JSON Error"), (2, 1, {"payment": 100}, Machine.ERROR_NOT_FOUND)],
)
def test_buy_product_from_machine_error(
    tester,
    client,
    mid: int,
    pid: int,
    payment_json: Dict[str, Any],
    expected_error: str,
):
    _ = client.post(
        "/product/create",
        json={"product_name": "product_1", "product_price": 100.00},
    )
    _ = tester.create_machine(location="some_location", name="some_name")

    _ = tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )

    buy_product_response = tester.buy_product_from_machine(
        machine_id=mid, product_id=pid, json=payment_json
    )

    assert MachineTest.expect_error_from_response(
        response=buy_product_response, expected_error=expected_error
    )


def test_remove_product_from_machine(tester, client):
    _ = client.post(
        "/product/create",
        json={"product_name": "product_1", "product_price": 100.00},
    )
    _ = tester.create_machine(location="some_location", name="some_name")

    _ = tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )

    remove_response = tester.remove_product_from_machine(machine_id=1, product_id=1)

    log: Log = Log.make_from_response(remove_response)
    assert tester.no_error() and log.has_entry(broad="Machine", specific="Machine ID 1")


@pytest.mark.parametrize(
    "mid, pid, expected_error",
    [(1, 2, Machine.ERROR_REMOVE_PRODUCT), (2, 1, Machine.ERROR_NOT_FOUND)],
)
def test_remove_product_from_machine_fail(
    tester, client, mid: int, pid: int, expected_error: str
):
    _ = client.post(
        "/product/create",
        json={"product_name": "product_1", "product_price": 100.00},
    )
    _ = tester.create_machine(location="some_location", name="some_name")

    _ = tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )

    remove_response = tester.remove_product_from_machine(machine_id=mid, product_id=pid)

    assert MachineTest.expect_error_from_response(
        response=remove_response, expected_error=expected_error
    )


@pytest.mark.parametrize("machines_count", [1, 2, 3, 120])
def test_remove_machine(tester, machines_count: int):
    for machine_id in range(machines_count):
        _ = tester.create_machine(
            location="some_location", name=f"some_name_{machine_id}"
        )

    for machine_id in range(machines_count):
        _ = tester.remove_machine(machine_id=(machine_id + 1))
        assert tester.no_error()


def test_remove_machine_error(tester):
    remove_response = tester.remove_machine(machine_id=42)
    assert MachineTest.expect_error_from_response(
        response=remove_response, expected_error=Machine.ERROR_NOT_FOUND
    )
