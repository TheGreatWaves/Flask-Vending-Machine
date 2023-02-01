from typing import Any, Dict, Optional

from werkzeug.test import TestResponse

from tests.fixtures.tester import Tester, save_response


class MachineTester(Tester):
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
