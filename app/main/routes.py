from flask import jsonify

from app.main import bp


@bp.route("/", methods=["GET"])
def index():
    # noqa: ANN201
    return jsonify(Message="Vending machine goes brr")
