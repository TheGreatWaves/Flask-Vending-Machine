from app_context import app, db
from dataclasses import dataclass

#===================================#
#     INITILIAZATION OF TABLES      #
#===================================#

# Vending machine
@dataclass
class Machine( db.Model ):
    machine_id: int
    name: str

    machine_id = db.Column('user_id', db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    
    def __init__(self, name):
        self.name = name

#=============================#
#           Set up            #
#=============================#

def create():
    db.drop_all()
    db.create_all()

# Initialize all tables (Note this will also drop all previously existing tables)
if __name__ == '__main__':  
    with app.app_context():
        create()