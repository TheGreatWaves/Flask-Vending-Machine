"""
This file contains the static initialization of the flask application.
All configurations and settings will be setup in this file.

All you need to import from this file is the app and db.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import yaml

# Flask app and a SQLAlchemy object for interacting with db
app = Flask(__name__) 

# Load credentials
cred = yaml.load(open('cred.yaml'), Loader=yaml.Loader)

# Connecting the application to the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' \
    + cred['mysql_user'] + ':' \
    + cred['mysql_password'] + '@' \
    + cred['mysql_host'] + '/' \
    + cred['mysql_db']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)



