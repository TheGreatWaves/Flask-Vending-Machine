from typing import Any, Optional
from dataclasses import dataclass

# Extremely explicit aliases
ResultMessage = str

@dataclass
class Result:
    object: Optional[Any]
    message: ResultMessage

    def __init__(self, _obj : Optional[Any], _message: str):
        self.object = _obj
        self.message = _message

    # For attribute unpacking
    def __iter__(self):
        return iter(self.__dict__.values())\

    @staticmethod 
    def error(err: str) -> "Result":
        return Result(None, err)

