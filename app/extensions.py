"""
Extensions for the flask app.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_swagger_ui import get_swaggerui_blueprint

db = SQLAlchemy()
csrf = CSRFProtect()

SWAGGER_URL = '/api/docs'
API_URL = '/static/apidocs.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Test application"
    }
)