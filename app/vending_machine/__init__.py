from flask import Blueprint
bp = Blueprint( 'vending_machine', __name__, url_prefix="/machine" )
from app.vending_machine import routes