"""
Copyright (c) 2021 Philipp Scheer
"""


import traceback
from datetime import datetime


class Logger:
    default_file = None

    def __init__(self, filename: str, print: bool=True) -> None:
        Logger.default_file = filename
        self.f = open(filename, "a+")
        self.print = print

    def error(self, msg, **kwargs):
        self.writeLogLine(f"error - {msg}\n{traceback.format_exc()}", **kwargs)

    def info(self, msg, **kwargs):
        self.writeLogLine(f"info - {msg}", **kwargs)

    def warning(self, msg, **kwargs):
        self.writeLogLine(f"warning - {msg}", **kwargs)

    def writeLogLine(self, line, **kwargs):
        additional_data = ""
        if len(kwargs) > 0:
            additional_data = " - {" + "; ".join([f"{x}={y}" for x,y in kwargs.items()]) + "}"
        line = f"{str(datetime.now())} - {line}{additional_data}"
        print(line)
        self.f.write(line + "\n")
        self.f.flush()
    
    @classmethod
    def default(cls):
        return Logger(Logger.default_file) if Logger.default_file is not None else None