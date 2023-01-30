from typing import Optional

import pytest

from app import db
from app.models.vending_machine import Machine


@pytest.mark.parametrize(
    "machine_name, machine_location",
    [
        ("John Estate", "Rick"),
        ("Antarctica", "James"),
        ("Mars", "GSDE4A"),
        ("Atlantis", "John"),
    ],
)
def test_make(app, machine_name: str, machine_location: str):
    with app.app_context():
        machine, msg = Machine.make(location=machine_location, name=machine_name)

        assert (
            machine
            and msg
            == f"Successfully added vending machine named '{machine_name}' at '{machine_location}'!"
        )


@pytest.mark.parametrize(
    "machine_name, machine_location, expected_err",
    [
        ("John Estate", 12.2, "Location can not be a number."),
        (134, "Wow estate", "Name can not be a number."),
        (
            "taken",
            "taken",
            "A machine with given name and location already exists. (Location: taken, Name: taken)",
        ),
    ],
)
def test_make_fail(app, machine_name: str, machine_location: str, expected_err: str):
    with app.app_context():
        taken, _ = Machine.make(location="taken", name="taken")
        db.session.add(taken)
        db.session.commit()

        success, err = Machine.make(location=machine_location, name=machine_name)

        assert not success and err == expected_err


@pytest.mark.parametrize(
    "machine_name, machine_location",
    [
        ("John Estate", "Rick"),
        ("Antarctica", "James"),
        ("Mars", "GSDE4A"),
        ("Atlantis", "John"),
    ],
)
def test_find_by_name(app, machine_name: str, machine_location: str):
    with app.app_context():
        taken, _ = Machine.make(location=machine_location, name=machine_name)
        db.session.add(taken)
        db.session.commit()

        found: Machine = Machine.find_by_name(machine_name)
        assert (
            found.machine_id == 1
            and found.machine_name == machine_name
            and found.location == machine_location
        )


@pytest.mark.parametrize(
    "machine_name, machine_location, expected",
    [
        (None, None, None),
        ("some_name_1", "some_location", Machine),
        (None, "some_location", list),
        ("some_name_1", None, Machine),
    ],
)
def test_find(
    app, machine_name: Optional[str], machine_location: Optional[str], expected
):
    with app.app_context():
        machine, _ = Machine.make(location="some_location", name="some_name_1")
        machine_2, _ = Machine.make(location="some_location", name="some_name_2")
        db.session.add(machine)
        db.session.add(machine_2)
        db.session.commit()

        result = Machine.find(name=machine_name, location=machine_location)

        if expected is None:
            assert result is None
        else:
            assert isinstance(result, expected)
