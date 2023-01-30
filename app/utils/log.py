from dataclasses import dataclass
from typing import Dict, List, Optional, TypeAlias

from flask import Response

from app.utils.result import Result

"""
Records stores a list of information about specific items
"""
from werkzeug.test import TestResponse

RecordsType: TypeAlias = Dict[str, List[str]]


@dataclass
class Record:
    records: RecordsType

    def __init__(self, records: Optional[RecordsType] = None):  # noqa: ANN204
        if records:
            self.records = records
        else:
            self.records = {}

    def __iadd__(self, other: "Record") -> "Record":
        for k, v in other.records.items():
            if record := self.records.get(k):
                record.extend(v)
            else:
                self.records[k] = v
        return self

    def add(self, specific: str, new_record: str) -> None:

        if record := self.records.get(specific):
            record.append(new_record)
        else:
            self.records[specific] = [new_record]

    def get(self, specific: str) -> List[str]:
        return self.records.get(specific)


"""
A log contains a bunch of broad entries which contains records regarding the entry
An example of a broad entry: "Error", one of the records specific entry could be: "Machine Error"
It can be used in conjuction with the Result class to help ease of logging (somewhat...)
"""

LogsType = Dict[str, Record]


@dataclass
class Log:
    logs: LogsType

    def __init__(self, log: Optional[LogsType] = None):  # noqa: ANN204
        if log:
            self.logs = log
        else:
            self.logs = {}

    # Creates a new broad entry. Note that
    # this returns a reference to the entry,
    # meaning we can directly call .add(<specific>, <info>)
    # without needing to supply the broad entry name again
    def entry(self, name: str) -> Record:
        if record := self.logs.get(name):
            return record
        else:
            self.logs[name] = Record(records={})
            return self.logs[name]

    # Add entry to name/specific
    def add(self, name: str, specific: str, info: str) -> "Log":
        if record := self.logs.get(name):
            record.add(specific, info)
        else:
            self.logs[name] = Record(records={specific: [info]})
        return self

    # Depending on the outcome of the result, if postive, the log will be added
    # accordingly to the entry specified, otherwise it will be under Error/<err_name>
    def add_result(
        self, name: str, specific: str, result: Result, err_name: Optional[str] = None
    ) -> "Log":
        success = result.object
        msg = result.message

        if success:
            if record := self.logs.get(name):
                record.add(specific, msg)
            else:
                self.logs[name] = Record(records={specific: [msg]})
        else:
            if err_name:
                self.error(specific=err_name, err=msg)
            else:
                self.error(specific=specific, err=msg)

        return self

    # You can use the += operator on logs to join them
    def __iadd__(self, other: "Log") -> "Log":
        for k, v in other.logs.items():
            if self.logs.get(k):
                self.logs[k] += v
            else:
                self.logs[k] = v
        return self

    # Built-in for ease of logging errors
    def error(self, specific: str, err: str) -> "Log":
        return self.add("Error", specific, err)

    @staticmethod
    def make_from_response(response: Response | TestResponse) -> "Log":
        log: Log = Log()

        if not isinstance(response.json, dict):
            return log

        raw_logs: Dict = response.json.get("logs")

        if raw_logs is None:
            return log

        for broad, broad_records in raw_logs.items():
            broad_entry: Record = log.entry(broad)
            record = broad_records.get("records")
            for specific, records in record.items():
                broad_entry.records[specific] = records
        return log

    def has_entry(self, broad: str, specific: Optional[str] = None) -> bool:

        if broad not in self.logs:
            return False

        if specific:
            if self.logs[broad].get(specific):
                return True
            else:
                return False

        return True

    def has_error(self, specific: Optional[str] = None) -> bool:
        return self.has_entry(broad="Error", specific=specific)
