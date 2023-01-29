from app import create_app, reset_db
from app.models.vending_machine import Machine

def test_create_app():
    app = create_app()
    reset_db(app=app)
    all_machine_instances_count = len(Machine.query.all())
    assert all_machine_instances_count == 0

    



