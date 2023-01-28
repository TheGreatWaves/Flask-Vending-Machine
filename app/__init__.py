"""
This package contains function for creating the app and resetting the database.
"""

from flask import Flask

from app.extensions import db
from config import Config


def create_app(config_class: Config = Config) -> Flask:
    app = Flask(__name__)

    # Load config over
    app.config.from_object(config_class)

    # Register db ( deferred initialization )
    db.init_app(app=app)

    # Blueprint registration
    from app.main import bp as main_bp
    from app.product import bp as product_bp
    from app.vending_machine import bp as machine_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(machine_bp)
    app.register_blueprint(product_bp)

    return app


def reset_db(app: Flask) -> None:
    with app.app_context():
        db.drop_all()
        db.create_all()
