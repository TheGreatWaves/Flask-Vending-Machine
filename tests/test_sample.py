from app import create_app, reset_db
from app.models.vending_machine import Machine


def test_create_app() -> None:
    app = create_app()
    reset_db(app)

    with app.app_context():
        number_of_products = len(Machine.query.all())
        assert number_of_products == 0
