from typing import Any, Dict, Optional

from tests.fixtures.tester import Tester, save_response


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
