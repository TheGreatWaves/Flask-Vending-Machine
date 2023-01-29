"""
Program entry point.

Note that you will need to have docker running.
"""

if __name__ == "__main__":  # pragma: no cover
    from app import create_app

    flask_app = create_app()
    flask_app.run(debug=True)
