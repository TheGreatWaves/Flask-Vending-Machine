"""
Note: This will need to be executed everytime you
make any modifications to the database tables ( adding, editting tables, etc )
"""


from app import create_app, reset_db


if __name__ == '__main__':  
    reset_db( create_app() )