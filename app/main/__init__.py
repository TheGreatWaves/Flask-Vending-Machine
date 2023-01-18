"""
Note: This template is VERY important.
      The order matters.
"""

from flask import Blueprint
bp = Blueprint( 'main', __name__ )
from app.main import routes