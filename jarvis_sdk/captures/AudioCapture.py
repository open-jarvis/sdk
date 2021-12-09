"""
Copyright (c) 2021 Philipp Scheer
"""


from dataclasses import dataclass

from jarvis_sdk import Intent


@dataclass
class AudioCapture:
    transcription: str = ""
    intent: Intent = None
    wave_audio: bytes = None

    def setTranscription(self, transcription):
        assert isinstance(transcription, str), "transcription must be of type str"
        self.transcription = transcription
    
    def setIntent(self, intent):
        assert isinstance(intent, Intent), "intent must be of type Intent"
        self.intent = intent