"""
Program entry point.
"""

from app import create_app

if __name__ == '__main__':  

    # Create the app and run it
    flask_app = create_app()
    flask_app.run(debug=True)
