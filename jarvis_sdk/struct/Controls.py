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
    channels: int
    rate: int

    def json(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "index": self.index,
            "channels": self.channels,
            "rate": self.rate,
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
            "default_input": self.default_input.json() if isinstance(self.default_input, AudioDevice) else self.default_input,
            "available_outputs": [_.json() for _ in self.available_outputs],
            "default_output": self.default_output.json() if isinstance(self.default_output, AudioDevice) else self.default_output,
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
    version: str
    hardware_id: str
    architecture: int
    cores: int
    ram: int
    audio: AudioInformation
    video: VideoInformation

    # additional
    timestamp: float = time.time()

    def json(self):
        return {
            "hardware_id": self.hardware_id,
            "version": self.version,
            "architecture": self.architecture,
            "cores": self.cores,
            "ram": self.ram,
            "audio": self.audio.json() if isinstance(self.audio, AudioInformation) else self.audio,
            "video": self.video.json() if isinstance(self.video, VideoInformation) else self.video,
            "timestamp": self.timestamp
        }

    @classmethod
    def object(cls, json: dict):
        return SystemInformation(**json) if json is not None else None



@dataclass
class Plugin:
    id: str
    version: str
    name: str
    online: bool
    enabled: bool

    def json(self):
        return {
            "id": self.id,
            "version": self.version,
            "name": self.name,
            "online": self.online,
            "enabled": self.enabled
        }
    
    @classmethod
    def object(cls, data: dict):
        return Plugin(**data)

@dataclass
class PluginInformation:
    plugins: list

    def json(self):
        return {
            "plugins": [_.json() for _ in self.plugins]
        }

    @classmethod
    def object(cls, data: dict):
        return PluginInformation(plugins=[Plugin(**_) for _ in (data or {"plugins": []}).get("plugins", []) ])

