"""
Copyright (c) 2021 Philipp Scheer
"""


import os
import json
import time
import copy
import pickle
from dataclasses import dataclass

from jarvis_sdk import AudioCapture


@dataclass
class Context:
    history: list
    data: dict
    default: None

    def __init__(self) -> None:
        self.history = list()
        self.data = dict()

    def set(self, key, value, assertType=None):
        if assertType is not None:
            assert isinstance(value, assertType), f"value {value} must be of type {assertType}"
        if key not in self.data:
            self.data[key] = []
        self.data[key].append({
            "timestamp": int(time.time()),
            "value": value
        })

    def get(self, key, default=None, atTimestamp: float=None):
        d = copy.deepcopy(self.data.get(key, []))
        if len(d) == 0:
            return default
        if atTimestamp is not None:
            d.reverse() # oldest entries last
            for val in d:
                if val.get("timestamp") < atTimestamp:
                    return val.get("value")
        return d[-1].get("value")

    def addAudioCapture(self, audioCapture: AudioCapture):
        assert isinstance(audioCapture, AudioCapture), "audioCapture must be of instance AudioCapture"
        self.history.append(audioCapture)

    def save(self, path):
        pickle.dump(self, open(path, "w"))

    def json(self):
        try:
            return json.dumps({
                "history": self.history,
                "data": self.data
            })
        except Exception:
            return None

    @classmethod
    def init(cls, path):
        # TODO: pickle is not secure
        if os.path.isfile(path):
            return pickle.load(open(path, "r"))
        return Context()
