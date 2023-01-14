from flask import Blueprint

bp = Blueprint('vending_machine', __name__)

from app.vending_machine import routes