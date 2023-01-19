from typing import List, Dict, Optional
from dataclasses import dataclass

from app.utils.result import Result

@dataclass 
class Record:
    Records: Dict[str, List[str]]

    def __init__(self) -> None:
        self.Records = {}

    def __init__(self, records):
        self.Records = records

    def __iadd__(self, other: "Record"):
        for k, v in other.Records.items():
            if record := self.Records.get(k):
                record.extend(v)
            else:
                self.Records[k] = v

    def add(self, specific:str, new_record: str):

        if record := self.Records.get(specific):
            record.append(new_record)
        else:
            self.Records[specific] = [new_record]

@dataclass
class Log:
    Logs: Dict[str, Record]

    def __init__(self):
        self.Logs = {}

    def entry(self, name:str):
        if record := self.Logs.get(name):
            return record
        else:
            self.Logs[name] = Record(records={})
            return self.Logs[name]

    def add(self, name:str, specific:str, info:str) -> "Log":
        if record := self.Logs.get(name):
            record.add(specific, info)
        else:
            self.Logs[name] = Record(records={specific:[info]})
        return self
    
    def addResult(self, name:str, specific:str, result: Result, err_name: Optional[str] = None) -> "Log":
        success = result.object
        msg = result.message

        if success:
            if record := self.Logs.get(name):
                record.add(specific, msg)
            else:
                self.Logs[name] = Record(records={specific:[msg]})
            return self
        else:
            if err_name:
                self.error(specific=err_name, err=msg)
            else:
                self.error(specific=specific, err=msg)

        return self

    def __iadd__(self, other: "Log"):
        print(other)
        for k, v in other.Logs.items():
            if record := self.Logs.get(k):
                record += v
            else:
                self.Logs[k] = v
        return self

    def error(self, specific:str, err: str) -> "Log":
        return self.add("Error", specific, err)