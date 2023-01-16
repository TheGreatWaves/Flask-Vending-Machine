"""
Program entry point.
Note that you will need to have docker running.
"""


from app import create_app


if __name__ == '__main__':  
    flask_app = create_app()
    flask_app.run(debug=True)
