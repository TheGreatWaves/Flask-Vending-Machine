"""
Program entry point.
"""

if __name__ == '__main__':  
    from entry_points import app
    # app.get("application").run
    app.run(debug=True)
