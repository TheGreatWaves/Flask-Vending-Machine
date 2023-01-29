from flask import Blueprint

bp = Blueprint("product", __name__, url_prefix="/product")
from app.product import routes  # noqa: F401, E402
