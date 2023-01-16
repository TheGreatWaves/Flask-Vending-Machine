from flask import Flask
from config import Config
from app.extensions import db

blueprints = []

def add_blueprint(bp):
    blueprints.append(bp)

def register_blueprints(app: Flask):
    print(f"Size: {len(blueprints)}")
    for bp in blueprints:
        app.register_blueprint(bp)


# Creates a flask app with configurations
# loaded from root/config.py
def create_app(config_class=Config):
    app = Flask(__name__)

    # Load config over
    app.config.from_object(config_class)

    # Register db ( deferred initialization )
    db.init_app(app=app)

    # Blueprint registration
    from app.main import bp as main_bp
    from app.vending_machine import bp as machine_bp
    from app.product import bp as product_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(machine_bp)
    app.register_blueprint(product_bp)

    with app.app_context():
        db.drop_all()
        db.create_all()

    return app