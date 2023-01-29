def test_main_route(client):  # noqa: ANN001, ANN201
    response = client.get("/")
    assert response.json.get("Message") == "Vending machine goes brr"
