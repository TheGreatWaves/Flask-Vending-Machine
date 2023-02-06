from dataclasses import dataclass
from typing import Optional

from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from app.utils.log import Log


@dataclass
class Tester:
    __test__ = False
    client: FlaskClient
    prev_response: TestResponse = None
    log: Log = None

    def no_error(self) -> bool:
        return not self.log.has_error()

    def expect_error(
        self, expected_error: Optional[str] = None, value: Optional[str] = None
    ):
        return self.log.has_error(specific=expected_error, value=value)

    def log_has_entry(
        self, broad: str, specific: Optional[str] = None, value: Optional[str] = None
    ):
        return self.log.has_entry(broad=broad, specific=specific, value=value)

    def response_has(self, **values):  # noqa: ANN003
        return response_has(response=self.prev_response, **values)

    @staticmethod
    def expect_error_from_response(
        response: TestResponse,
        expected_error: Optional[str] = None,
        value: Optional[str] = None,
    ) -> bool:
        return Log.make_from_response(response=response).has_error(
            specific=expected_error, value=value
        )

    def debug(self):
        print(self.prev_response.json)


# A decorator used to save response to tester
def save_response(func):
    def wrapper(self, *args, **kwargs):  # noqa: ANN002, ANN003
        response = func(self, *args, **kwargs)
        self.prev_response = response
        self.log = Log.make_from_response(response)
        return response

    return wrapper


def response_has(response: TestResponse, **values):  # noqa: ANN003
    response_json = response.json

    # If it is a list, we'll just check the head
    if isinstance(response.json, list):
        response_json = response_json[0]

    for k, v in values.items():
        if response_json.get(k) != v:
            return False
    return True
