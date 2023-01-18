from app.main import bp
from flask import jsonify


@bp.route("/", methods=['GET'])
def index():
    return jsonify(Message="Vending machine goes brr")
