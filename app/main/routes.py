from flask import Response, jsonify

from app.main import bp


@bp.route("/", methods=["GET"])
def index() -> Response:
    return jsonify(Message="Vending machine goes brr")
