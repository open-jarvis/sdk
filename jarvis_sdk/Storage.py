"""
Copyright (c) 2021 Philipp Scheer
"""


import os
import time
import json


class Storage:
    FILENAME = "storage.json"
    PATH = "./"


    @staticmethod
    def get(key: str, default: any = None):
        Storage.check_file()
        val = json.load(open(Storage.PATH + "/" + Storage.FILENAME, "r+"))
        return val.get(key, default)

    @staticmethod
    def set(key: str, value: any):
        Storage.check_file()
        val = json.load(open(Storage.PATH + "/" + Storage.FILENAME, "r+"))
        val[key] = value
        json.dump(val, open(Storage.PATH + "/" + Storage.FILENAME, "w+"))

    @staticmethod
    def check_file():
        if not os.path.exists(Storage.PATH + "/" + Storage.FILENAME):
            with open(Storage.PATH + "/" + Storage.FILENAME, "w+") as f:
                json.dump({}, f)


class Session:
    def __init__(self) -> None:
        self.data = {}
    
    def __getattr__(self, key: str):
        item = self.data.get(key, {})
        if item.get("expires", time.time() - 1) < time.time():
            return None
        return item.get("value", None)
    
    def get(self, key: str):
        return self.__getattr__(key)

    def set(self, key: str, value, expires: int = 60 * 60 * 1):
        self.data[key] = {  "value": value,
                            "expires": int(time.time() + expires) }

