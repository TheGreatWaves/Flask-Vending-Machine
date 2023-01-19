"""
Commonly used aliases 
"""

from app.utils.log import Log

JSON_ERROR = Log().error("JSON Error", "Invalid JSON body")

def isnumber(s: str) -> bool:
    if isinstance(s, int): return True
    return s.replace('.','',1).isdigit()