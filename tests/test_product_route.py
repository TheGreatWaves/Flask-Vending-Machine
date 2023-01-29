import pytest

from app.extensions import db
from app.models.product import Product
from app.utils.log import Log


@pytest.mark.parametrize(
    "product_name,product_price",
    [("some_name", 123.0), ("HeyMANWHATSUP", 91232), ("Brrr", 0.12)],
)
def test_product_creation(app, client, product_name, product_price):
    # product_name = "sample_name"
    # product_price = 100.0
    response = client.post(
        "/product/create",
        json={"product_name": product_name, "product_price": product_price},
    )
    assert not Log.make_from_response(response=response).has_error()

    log: Log = Log.make_from_response(response=response)
    assert log.has_entry(
        broad="Product", specific=f"New Product: {product_name}, {product_price}"
    )

    with app.app_context():
        product: Product = db.session.get(Product, {"product_id": 1})
        assert product is not None
        assert product.product_name == product_name and float(
            product.product_price
        ) == float(product_price)

        db.session.delete(product)
        db.session.commit()

        assert db.session.get(Product, {"product_id": 1}) is None


def test_product_creation_error(app, client):
    product_name = "sample_name"
    product_price = 100.0
    _ = client.post(
        "/product/create",
        json={"product_name": product_name, "product_price": product_price},
    )
    fail_response = client.post(
        "/product/create",
        json={"product_name": product_name, "product_price": product_price},
    )

    assert Log.make_from_response(response=fail_response).has_error(
        Product.ERROR_CREATE_FAIL
    )


def test_product_creation_json_error(app, client):
    fail_response = client.post("/product/create", json={})
    assert Log.make_from_response(response=fail_response).has_error("JSON Error")


def test_search_product_1(app, client):
    product_name = "sample_name"
    product_price = 100.00
    response = client.post(
        "/product/create",
        json={"product_name": product_name, "product_price": product_price},
    )
    assert not Log.make_from_response(response=response).has_error()

    with app.app_context():
        product: Product = db.session.get(Product, {"product_id": 1})
        assert product is not None

    response = client.get(f"product/search/{product_name}")
    response_json = response.json[0]

    assert (
        response_json.get("product_id") == 1
        and response_json.get("product_name") == str(product_name)
        and response_json.get("product_price")[:-1] == str(product_price)
    )


def test_search_product_2(app, client):
    _ = client.post(
        "/product/create", json={"product_name": "product_1", "product_price": 100.00}
    )
    _ = client.post(
        "/product/create", json={"product_name": "product_2", "product_price": 100.00}
    )

    search_response = client.get("product/search/product")
    assert len(search_response.json) == 2

    _ = client.post(
        "/product/create", json={"product_name": "product_3", "product_price": 100.00}
    )

    search_response = client.get("product/search/product")
    assert len(search_response.json) == 3


def test_search_product_not_found(app, client):
    search_response = client.get("product/search/product")
    log: Log = Log.make_from_response(response=search_response)
    assert log.has_error(Product.ERROR_NOT_FOUND)


def test_get_product(app, client):
    response = client.get("/product/1")
    log: Log = Log.make_from_response(response=response)
    assert log.has_error(specific=Product.ERROR_NOT_FOUND)

    product_name = "sample_name"
    product_price = 100.00
    _ = client.post(
        "/product/create",
        json={"product_name": product_name, "product_price": product_price},
    )

    response = client.get("/product/1")
    response_json = response.json
    log: Log = Log.make_from_response(response=response)

    assert not log.has_error()
    assert (
        response_json.get("product_id") == 1
        and response_json.get("product_name") == str(product_name)
        and response_json.get("product_price")[:-1] == str(product_price)
    )


def test_edit_product(app, client):
    original_name = "product_1"
    original_price = 100.00
    new_name = "new_product_1"
    new_price = 200.0

    create_response = client.post(
        "/product/create",
        json={"product_name": original_name, "product_price": original_price},
    )

    assert not Log.make_from_response(response=create_response).has_error()

    response_json = client.get("/product/1").json

    assert (
        response_json.get("product_id") == 1
        and response_json.get("product_name") == str(original_name)
        and response_json.get("product_price")[:-1] == str(original_price)
    )

    edit_response = client.post(
        "/product/1/edit", json={"product_name": new_name, "product_price": new_price}
    )

    edit_log: Log = Log.make_from_response(response=edit_response)

    assert not edit_log.has_error()
    assert edit_log.has_entry(broad="Product", specific="Product ID 1")

    response_json = client.get("/product/1").json

    assert (
        response_json.get("product_id") == 1
        and response_json.get("product_name") == str(new_name)
        and response_json.get("product_price")[:-1] == str(new_price)
    )


def test_edit_product_fail(app, client):
    # Product not found
    edit_response = client.post("/product/1/edit", json={})
    assert Log.make_from_response(response=edit_response).has_error(
        Product.ERROR_NOT_FOUND
    )

    original_name = "product_1"
    original_price = 100.00
    create_response = client.post(
        "/product/create",
        json={"product_name": original_name, "product_price": original_price},
    )
    assert not Log.make_from_response(response=create_response).has_error()

    # Redundant name and price
    edit_response = client.post(
        "/product/1/edit",
        json={"product_name": original_name, "product_price": original_price},
    )
    assert Log.make_from_response(response=edit_response).has_error(
        Product.ERROR_EDIT_FAIL
    )

    # Invalid JSON body
    edit_response = client.post("/product/1/edit", json={})
    assert Log.make_from_response(response=edit_response).has_error("JSON Error")


def test_get_all_products(app, client):
    for product_num in range(10):
        create_response = client.post(
            "/product/create",
            json={"product_name": f"product_{product_num}", "product_price": 100.0},
        )
        assert not Log.make_from_response(response=create_response).has_error()

    get_all_response = client.get("/product/all")

    assert len(get_all_response.json) == 10

    for product_num in range(10):
        get_response = client.get(f"/product/{product_num + 1}")
        assert not Log.make_from_response(response=get_response).has_error()


def test_get_all_products_fail(app, client):
    get_all_response = client.get("/product/all")
    assert Log.make_from_response(response=get_all_response).has_error(
        Product.ERROR_NOT_FOUND
    )


def test_get_machine_with_product(app, client):
    from app.models.vending_machine_stock import MachineStock

    product_id = 1
    create_response = client.post(
        "/product/create",
        json={"product_name": f"product_{product_id}", "product_price": 100.0},
    )
    assert not Log.make_from_response(response=create_response).has_error()

    with app.app_context():
        for machine_id in range(10):
            create_machine_response = client.post(
                f"machine/create/location_{machine_id}/John"
            )
            assert not Log.make_from_response(
                response=create_machine_response
            ).has_error()

            stock, _ = MachineStock.make(
                product_id=product_id, machine_id=machine_id + 1, quantity=10
            )
            assert stock is not None

            db.session.add(stock)
        db.session.commit()

    get_machines_response = client.get(f"/product/{product_id}/where")
    assert len(get_machines_response.json) == 10

    for machine_id in range(10):
        machine = get_machines_response.json[machine_id]
        assert (
            machine.get("location") == f"location_{machine_id}"
            and machine.get("machine_name") == "John"
        )


def test_get_machine_with_product_fail(app, client):
    # product not found
    not_found_response = client.get("/product/42/where")
    assert Log.make_from_response(response=not_found_response).has_error(
        Product.ERROR_NOT_FOUND
    )

    _ = client.post(
        "/product/create", json={"product_name": "product_1", "product_price": 100.0}
    )

    # product not found in any machine
    no_machine_response = client.get("/product/1/where")
    assert Log.make_from_response(response=no_machine_response).has_error(
        Product.ERROR_NOT_FOUND
    )
