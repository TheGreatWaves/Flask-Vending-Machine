import pytest

from app import create_app, reset_db
from config import Config


class AppTestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = (
        "mysql://root:vending_test_pass@127.0.0.1:13311/vending_test_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture()
def app():
    app = create_app(config_class=AppTestConfig)
    reset_db(app=app)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
