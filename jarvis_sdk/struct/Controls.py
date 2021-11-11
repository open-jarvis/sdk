"""
Copyright (c) 2021 Philipp Scheer
"""


import time
from dataclasses import dataclass


@dataclass
class AudioDevice:
    type: str
    index: int
    name: str

    def json(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "index": self.index,
        }
    
    @classmethod
    def object(cls, data: dict):
        return AudioDevice(**data)


@dataclass
class AudioInformation:
    available_inputs: list # of AudioDevice
    default_input: int
    available_outputs: list # of AudioDevice
    default_output: int

    timestamp: float = time.time()

    def json(self) -> dict:
        return {
            "available_inputs": [_.json() for _ in self.available_inputs],
            "default_input": self.default_input,
            "available_outputs": [_.json() for _ in self.available_outputs],
            "default_output": self.default_output,
            "timestamp": self.timestamp
        }
    


@dataclass
class VideoInformation:
    def json(self) -> dict:
        return {}



@dataclass
class Raw:
    value: any

    def json(self):
        return self.value


@dataclass
class Uptime:
    alive_since: float
    timestamp: float = time.time()

    def json(self):
        return {
            "timestamp": self.timestamp,
            "alive_since": self.alive_since
        }

    @classmethod
    def object(cls, json: dict):
        return Uptime(**json) if json is not None else None


@dataclass
class SystemInformation:
    # software
    plugins: list
    version: str

    # hardware
    hardware_id: str
    architecture: int
    cores: int
    ram: int
    audio: AudioInformation
    # video: VideoInformation

    # additional
    timestamp: float = time.time()

    def json(self):
        return {
            "hardware_id": self.hardware_id,
            "plugins": self.plugins,
            "version": self.version,
            "architecture": self.architecture,
            "cores": self.cores,
            "ram": self.ram,
            "audio": self.audio.json() if isinstance(self.audio, AudioInformation) else self.audio,
            # "video": self.video.json() if isinstance(self.video, VideoInformation) else self.video,
            "timestamp": self.timestamp
        }

    @classmethod
    def object(cls, json: dict):
        return SystemInformation(**json) if json is not None else None
