from dataclasses import dataclass
from typing import Any, Iterator, Optional

# Extremely explicit aliases
ResultMessage = str


@dataclass
class Result:
    object: Optional[Any]
    message: ResultMessage

    def __init__(self, _obj: Optional[Any], _message: str):  # noqa: ANN204
        self.object = _obj
        self.message = _message

    # For attribute unpacking
    def __iter__(self: "Result") -> Iterator:
        return iter(self.__dict__.values())

    # The two static methods below can be used for
    # methods/functions which only returns a message,
    # but requires a way to indicate whether the
    # function failed or succeeded.

    @staticmethod
    def error(err: str) -> "Result":
        return Result(None, err)

    @staticmethod
    def success(msg: str) -> "Result":
        return Result(True, msg)
