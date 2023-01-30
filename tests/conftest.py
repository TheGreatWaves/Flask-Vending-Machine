from dataclasses import dataclass
from typing import Optional

import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from app import create_app, reset_db
from app.utils.log import Log
from config import Config


class AppTestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


@pytest.fixture()
def app():
    app = create_app(config_class=AppTestConfig)
    reset_db(app=app)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@dataclass
class Tester:
    __test__ = False
    client: FlaskClient

    @staticmethod
    def no_error(response: TestResponse) -> bool:
        return not Log.make_from_response(response=response).has_error()

    @staticmethod
    def expect_error(
        response: TestResponse, expected_error: Optional[str] = None
    ) -> bool:
        return Log.make_from_response(response=response).has_error(expected_error)
