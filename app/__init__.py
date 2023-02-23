"""
This package contains function for creating the app and resetting the database.
"""

from flask import Flask

from app.extensions import csrf, db
from config import Config


def create_app(config_class: Config = Config) -> Flask:
    app = Flask(__name__, static_folder='../static')

    # CSRF protection
    # csrf.init_app(app=app)

    # Load config over
    app.config.from_object(config_class)

    # Register db ( deferred initialization )
    db.init_app(app=app)

    # Blueprint registration
    from app.main import bp as main_bp
    from app.product import bp as product_bp
    from app.vending_machine import bp as machine_bp
    from app.extensions import swaggerui_blueprint as swag_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(machine_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(swag_bp)

    return app


def reset_db(app: Flask) -> None:
    with app.app_context():
        db.drop_all()
        db.create_all()
