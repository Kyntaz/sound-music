from Audio import Audio
import numpy as np

class Event:
    def __init__(self, data: np.array, kind: str):
        self.data = data
        self.type = kind

class EventExtractor:
    def extract(self, audio: Audio) -> list:
        pass