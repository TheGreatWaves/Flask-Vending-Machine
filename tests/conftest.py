import pytest

from app import create_app, reset_db


@pytest.fixture()
def app():
    app = create_app()

    app.config.update(
        {
            "TESTING": True,
        }
    )
    reset_db(app=app)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
