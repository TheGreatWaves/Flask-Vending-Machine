"""
Note: This will need to be executed everytime you.

make any modifications to the database tables ( adding, editting tables, etc )
"""

if __name__ == "__main__":  # pragma: no cover
    from app import create_app, reset_db

    reset_db(create_app())
