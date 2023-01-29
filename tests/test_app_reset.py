from app import reset_db
from app.extensions import db
from app.models.vending_machine import Machine


def test_create_fresh_app(app):
    reset_db(app)
    with app.app_context():
        number_of_products = len(Machine.query.all())
        number_of_machines = len(Machine.query.all())
        assert number_of_products == 0 and number_of_machines == 0

def test_app_db_drop(app):
    with app.app_context():
        machine, _ = Machine.make("some_location", "some_name")
        db.session.add(machine)
        db.session.commit()

        number_of_machines = len(Machine.query.all())

        assert number_of_machines == 1

        machine.destroy()
        db.session.commit()
        number_of_machines = len(Machine.query.all())

        assert number_of_machines == 0