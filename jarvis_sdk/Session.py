"""
Copyright (c) 2021 Philipp Scheer
"""


import time
import json


class Session():
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