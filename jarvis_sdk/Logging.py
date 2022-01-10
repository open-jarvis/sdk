"""
Copyright (c) 2021 Philipp Scheer
"""


import traceback
from datetime import datetime


class Logger:
    default = None

    def __init__(self, filename: str, print: bool=True, attach: bool = False) -> None:
        self.f = open(filename, "a+")
        if not attach:
            self.f.write("\n" + "="*100 + "\n\n")
        self.print = print
        self.error = self._error
        self.info = self._info
        self.warning = self._warning
        Logger.default = self

    def _error(self, msg, **kwargs):
        self.writeLogLine(f"error - {msg}\n{traceback.format_exc()}", **kwargs)

    def _info(self, msg, **kwargs):
        self.writeLogLine(f"info - {msg}", **kwargs)

    def _warning(self, msg, **kwargs):
        self.writeLogLine(f"warning - {msg}", **kwargs)

    def writeLogLine(self, line, **kwargs):
        additional_data = ""
        if len(kwargs) > 0:
            additional_data = " - {" + "; ".join([f"{x}={y}" for x,y in kwargs.items()]) + "}"
        line = f"{str(datetime.now())} - {line}{additional_data}"
        print(line)
        self.f.write(line + "\n")
        self.f.flush()
    
    @staticmethod
    def error(msg, **kwargs):
        if Logger.default: Logger.default.error(msg, **kwargs)

    @staticmethod
    def info(msg, **kwargs):
        if Logger.default: Logger.default.info(msg, **kwargs)

    @staticmethod
    def warning(msg, **kwargs):
        if Logger.default: Logger.default.warning(msg, **kwargs)
