from dataclasses import dataclass
from typing import Any, Dict, Optional

import pytest
from werkzeug.test import TestResponse

from app.models.vending_machine import Machine
from app.utils.log import Log
from tests.conftest import Tester


@dataclass
class MachineTest(Tester):
    def create_machine(self, location: str, name: str) -> TestResponse:
        return self.client.post(f"/machine/create/{location}/{name}")

    def find_machine(self, location: str, name: Optional[str] = None) -> TestResponse:
        if name:
            return self.client.get(f"/machine/at/{location}/{name}")
        return self.client.get(f"/machine/at/{location}")

    def add_product_to_machine(
        self, machine_id: int, json: Dict[str, Any]
    ) -> TestResponse:
        return self.client.post(f"/machine/{machine_id}/add", json=json)


@pytest.mark.parametrize(
    "machine_location, machine_name",
    [
        ("John Estate", "Rick"),
        ("Antarctica", "James"),
        ("Mars", "GSDE4A"),
        ("Atlantis", "John"),
    ],
)
def test_create_machine(client, machine_location, machine_name):
    tester = MachineTest(client=client)
    create_response = tester.create_machine(machine_location, machine_name)
    assert MachineTest.no_error(create_response)


@pytest.mark.parametrize(
    "machine_location, machine_name",
    [("123", "123"), ("wow", 123.0), (12, "John"), ("Location", 23)],
)
def test_create_machine_fail(client, machine_location, machine_name):
    tester = MachineTest(client=client)
    create_response = tester.create_machine(machine_location, machine_name)
    assert MachineTest.expect_error(create_response, Machine.ERROR_CREATE_FAIL)


def test_get_machine(client):
    tester = MachineTest(client=client)
    for machine_id in range(1, 11):
        _ = tester.create_machine(f"location_{machine_id}", "some_name")

    # Make sure all can be found
    for search_machine_id in range(1, 11):
        search_response = tester.find_machine(
            f"location_{search_machine_id}", "some_name"
        )
        assert MachineTest.no_error(search_response)

    # Add 3 machines to some_location_1
    for i in range(3):
        _ = tester.create_machine("some_location_1", f"some_name_{i}")

    # Add 8 machines to some_location_6
    for i in range(8):
        _ = tester.create_machine("some_location_6", f"some_name_{i}")

    # Make sure we get all 3 machines added to some_location_1
    search_response = tester.find_machine("some_location_1")
    assert MachineTest.no_error(search_response) and len(search_response.json) == 3

    # Make sure we get all 8 machines added to some_location_1
    search_response = tester.find_machine("some_location_6")
    assert MachineTest.no_error(search_response) and len(search_response.json) == 8


def test_get_machine_fail(client):
    tester = MachineTest(client=client)
    search_response = tester.find_machine("some_location", "john")
    assert MachineTest.expect_error(search_response, Machine.ERROR_NOT_FOUND)


def test_add_product_to_machine(client):
    tester = MachineTest(client=client)
    _ = client.post(
        "/product/create",
        json={"product_name": "product_1", "product_price": 100.00},
    )
    _ = tester.create_machine(location="some_location", name="some_name")
    add_response = tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )
    assert MachineTest.no_error(add_response) and Log.make_from_response(
        response=add_response
    ).has_entry(broad="Product", specific="Product ID 1")


def test_add_product_to_machine_fail(client):
    tester = MachineTest(client=client)

    # Machine not found
    add_response = tester.add_product_to_machine(
        machine_id=1, json={"stock_list": [{"product_id": 1, "quantity": 10}]}
    )
    assert MachineTest.expect_error(add_response, Machine.ERROR_NOT_FOUND)

    # Invalid json
    _ = client.post(
        "/product/create",
        json={"product_name": "product_1", "product_price": 100.00},
    )
    _ = tester.create_machine(location="some_location", name="some_name")

    add_response = tester.add_product_to_machine(machine_id=1, json={})

    assert MachineTest.expect_error(response=add_response, expected_error="JSON Error")
