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

@dataclass
class AudioInformation:
    available_inputs: list # of AudioDevice
    default_input: int
    available_outputs: list # of AudioDevice
    default_output: int


@dataclass
class VideoInformation:
    pass



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
    def object(json: dict):
        return Uptime(**json)


@dataclass
class SystemInformation:
    # software
    plugins: list
    version: str

    # hardware
    architecture: int
    cores: int
    ram: int
    audio: AudioInformation
    # video: VideoInformation

    def json(self):
        return {
            "plugins": self.plugins,
            "version": self.version,
            "architecture": self.architecture,
            "cores": self.cores,
            "ram": self.ram,
            "audio": self.audio.json() if isinstance(self.audio, AudioInformation) else self.audio,
            # "video": self.video.json() if isinstance(self.video, VideoInformation) else self.video,
        }

    @classmethod
    def object(json: dict):
        return SystemInformation(**json)
