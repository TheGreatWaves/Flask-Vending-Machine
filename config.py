# Note that you WILL need to have the docker container running.
# Execute run_docker.sh to set it up and have it running.
# Once you do, the URI below should work perfectly.

mysql_user = "root"
mysql_password = "vendingpass"
mysql_host = "127.0.0.1:13310"
mysql_db = "vendingdb"

"""
Configuration details of the flask app
"""
class Config:
    SQLALCHEMY_DATABASE_URI = f'mysql://{ mysql_user }:{ mysql_password }@{ mysql_host }/{ mysql_db }'
    SQLALCHEMY_TRACK_MODIFICATIONS = False