from typing import Any, Dict, Optional

import pytest

from app.extensions import db
from app.models.product import Product
from app.utils.log import Log
from tests.conftest import Tester, save_response


class ProductTester(Tester):
    @save_response
    def create_product(
        self, product_name: Optional[str] = None, product_price: Optional[float] = None
    ):
        create = "/product/create"
        if product_name is None and product_price is None:
            return self.client.post(create, json={})

        return self.client.post(
            create, json={"product_name": product_name, "product_price": product_price}
        )

    @save_response
    def search_product(self, product_name: str):
        return self.client.get(f"product/search/{product_name}")

    @save_response
    def get(self, product_id: int):
        return self.client.get(f"/product/{product_id}")

    @save_response
    def edit_product(
        self,
        product_id: int,
        new_name: Optional[str] = None,
        new_price: Optional[float] = None,
    ):
        json: Dict[str, Any] = {}

        if new_name:
            json["product_name"] = new_name

        if new_price:
            json["product_price"] = new_price

        return self.client.post(f"/product/{product_id}/edit", json=json)

    @save_response
    def get_all_machines(self):
        return self.client.get("/product/all")

    @save_response
    def where_product(self, product_id: int):
        return self.client.get(f"/product/{product_id}/where")


@pytest.fixture
def tester(client):
    return ProductTester(client=client, prev_response=None)


def expect_error(response, err: str = None):
    return Log.make_from_response(response=response).has_error(err)


@pytest.mark.parametrize(
    "product_info",
    [
        {"product_name": "some_name", "product_price": 123.0},
        {"product_name": "hello", "product_price": 123.0},
        {"product_name": "wow", "product_price": 256},
    ],
)
def test_product_creation(tester, product_info):
    product_name = product_info["product_name"]
    product_price = product_info["product_price"]
    _ = tester.create_product(product_name=product_name, product_price=product_price)

    assert tester.no_error()

    assert tester.log_has_entry(
        broad="Product",
        specific=f"New Product: {product_name}, {product_price}",
        value=f"Successfully added product: [{product_name}, {float(product_price)}]",
    )


@pytest.mark.parametrize(
    "product_info, expected_err",
    [
        ({"product_name": 123, "product_price": 123.0}, "The name cannot be a number."),
        (
            {"product_name": "wow", "product_price": "what?"},
            "The price value is invalid. (Incorrect type, expected float, got=str)",
        ),
        ({"product_price": 123.0}, "Product name is missing."),
        ({"product_name": "name"}, "Product price is missing."),
        (
            {"product_name": "name", "product_price": -123.0},
            "Invalid price value. (price < 0.00)",
        ),
        (
            {"product_name": "taken", "product_price": 100.0},
            "A product with the given name already exists. (Product Name: taken)",
        ),
    ],
)
def test_product_creation_error(tester, product_info, expected_err):
    _ = tester.create_product(product_name="taken", product_price=100.0)
    product_name: str | float | None = product_info.get("product_name")
    product_price: float = product_info.get("product_price")

    _ = tester.create_product(product_name=product_name, product_price=product_price)
    assert tester.expect_error(
        expected_error=Product.ERROR_CREATE_FAIL, value=expected_err
    )


def test_product_creation_json_error(tester):
    _ = tester.create_product()
    assert tester.expect_error(expected_error="JSON Error", value="Invalid JSON body")


def test_search_product_1(tester):
    product_name = "sample_name"
    product_price = 100.25

    _ = tester.create_product(product_name=product_name, product_price=product_price)
    assert tester.no_error()

    _ = tester.search_product(product_name=product_name)
    assert tester.no_error()

    assert tester.response_has(
        product_id=1, product_name=str(product_name), product_price=str(product_price)
    )


def test_search_product_2(tester):
    _ = tester.create_product(product_name="product_1", product_price=100.00)
    assert tester.no_error()

    _ = tester.create_product(product_name="product_2", product_price=100.00)
    assert tester.no_error()

    search_response = tester.search_product(product_name="product")
    assert tester.no_error()
    assert len(search_response.json) == 2

    _ = tester.create_product(product_name="product_3", product_price=100.00)
    assert tester.no_error()

    search_response = tester.search_product(product_name="product")
    assert tester.no_error()
    assert len(search_response.json) == 3


@pytest.mark.parametrize(
    "product_name",
    ["product", "John", "Atlantis"],
)
def test_search_product_not_found(tester, product_name: str):
    _ = tester.search_product(product_name=product_name)
    assert tester.expect_error(
        expected_error=Product.ERROR_NOT_FOUND,
        value=f"Product not found. (Identifier: {product_name})",
    )


def test_get_product(tester):
    _ = tester.get(product_id=1)
    assert tester.expect_error(
        expected_error=Product.ERROR_NOT_FOUND,
        value="Product not found. (Product ID: 1)",
    )

    product_name = "sample_name"
    product_price = 100.25

    _ = tester.create_product(product_name=product_name, product_price=product_price)
    tester.no_error()

    _ = tester.get(product_id=1)
    assert tester.no_error()

    assert tester.response_has(
        product_id=1, product_name=str(product_name), product_price=str(product_price)
    )


def test_edit_product(tester):
    original_name = "product_1"
    original_price = 100.25
    new_name = "new_product_1"
    new_price = 200.25

    _ = tester.create_product(product_name=original_name, product_price=original_price)
    assert tester.no_error()

    _ = tester.get(product_id=1)
    assert tester.response_has(
        product_id=1, product_name=str(original_name), product_price=str(original_price)
    )

    _ = tester.edit_product(product_id=1, new_name=new_name, new_price=new_price)
    assert tester.no_error()
    assert tester.log_has_entry(broad="Product", specific="Product ID 1")

    _ = tester.get(product_id=1)
    assert tester.response_has(
        product_id=1, product_name=str(new_name), product_price=str(new_price)
    )


@pytest.mark.parametrize(
    "product_info, expected_err, value",
    [
        (
            {"product_id": 3, "product_name": "new_name", "product_price": 0.25},
            Product.ERROR_NOT_FOUND,
            "Product not found. (Product ID: 3)",
        ),
        (
            {"product_id": 1, "product_name": "some_name"},
            Product.ERROR_EDIT_FAIL,
            "Name redundant, no changes made.",
        ),
        (
            {"product_id": 1, "product_price": 200.25},
            Product.ERROR_EDIT_FAIL,
            "Price redundant, no changes made.",
        ),
        (
            {"product_id": 1, "product_name": None, "product_price": None},
            "JSON Error",
            "Invalid JSON body",
        ),
        (
            {"product_id": 1, "product_name": 123},
            Product.ERROR_EDIT_FAIL,
            "The name cannot be a number.",
        ),
        (
            {"product_id": 1, "product_name": "taken"},
            Product.ERROR_EDIT_FAIL,
            "An existing product with the name 'taken' already exists.",
        ),
        (
            {"product_id": 1, "product_price": "john"},
            Product.ERROR_EDIT_FAIL,
            "The price value is invalid. (Incorrect type, expected float, got=str)",
        ),
    ],
)
def test_edit_product_fail(tester, product_info, expected_err, value):
    _ = tester.create_product(product_name="some_name", product_price=200.25)
    assert tester.no_error()

    _ = tester.create_product(product_name="taken", product_price=100.25)
    assert tester.no_error()

    _ = tester.edit_product(
        product_id=product_info.get("product_id"),
        new_name=product_info.get("product_name"),
        new_price=product_info.get("product_price"),
    )
    assert tester.expect_error(expected_error=expected_err, value=value)


def test_edit_product_fail_2(tester, client):
    _ = tester.create_product(product_name="some_name", product_price=100.25)
    tester.no_error()

    # Nothing to edit
    edit_response = client.post(
        "/product/1/edit", json={"product_name": None, "product_price": None}
    )
    assert expect_error(response=edit_response, err=Product.ERROR_EDIT_FAIL)


def test_get_all_products(tester):
    # Add 10 products
    for product_num in range(10):
        _ = tester.create_product(
            product_name=f"product_{product_num}", product_price=100.25
        )
        assert tester.no_error()

    # Get all 10 products
    get_all_response = tester.get_all_machines()
    assert len(get_all_response.json) == 10

    # Try getting each individual products
    for product_num in range(10):
        _ = tester.get(product_id=product_num + 1)
        assert tester.no_error()


def test_get_all_products_fail(tester):
    _ = tester.get_all_machines()
    assert tester.expect_error(
        expected_error=Product.ERROR_NOT_FOUND, value="There are no existing products"
    )


def test_get_machine_with_product(tester, app, client):
    from app.models.vending_machine_stock import MachineStock

    product_id = 1
    _ = tester.create_product(product_name=f"product_{product_id}", product_price=100.0)
    assert tester.no_error()

    with app.app_context():
        for machine_id in range(10):
            create_machine_response = client.post(
                f"machine/create/location_{machine_id}/John"
            )
            assert not Tester.expect_error_from_response(create_machine_response)

            stock, _ = MachineStock.make(
                product_id=product_id, machine_id=machine_id + 1, quantity=10
            )
            assert stock is not None

            db.session.add(stock)
        db.session.commit()

    get_machines_response = tester.where_product(product_id=product_id)
    assert tester.no_error()
    assert len(get_machines_response.json) == 10

    for machine_id in range(10):
        machine = get_machines_response.json[machine_id]
        assert (
            machine.get("location") == f"location_{machine_id}"
            and machine.get("machine_name") == "John"
        )


def test_get_machine_with_product_fail(tester, app, client):
    # product not found
    _ = tester.where_product(product_id=42)
    assert tester.expect_error(
        expected_error=Product.ERROR_NOT_FOUND,
        value="Product not found. (Product ID: 42)",
    )

    _ = tester.create_product(product_name="product_1", product_price=100.0)
    assert tester.no_error()

    # product not found in any machine
    _ = tester.where_product(product_id=1)
    assert tester.expect_error(
        expected_error=Product.ERROR_NOT_FOUND,
        value="Product not found in any machine.",
    )
