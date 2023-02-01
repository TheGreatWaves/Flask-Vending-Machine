"""
Commonly used aliases
"""

from app.utils.log import Log

JSON_ERROR = Log().error("JSON Error", "Invalid JSON body.")


def isnumber(s: str) -> bool:
    if isinstance(s, int) or isinstance(s, float):
        return True

    number = s
    front = s[0]
    if front == "-":
        number = s[1:]

    return number.replace(".", "", 1).isdigit()
