from Music import Note
from EventExtraction import Event
from Architecture import SYSTEM

@SYSTEM.is_instrument
class Instrument:
    def __init__(self, event: Event, effects: list=[]):
        self.event = event
        self.type = event.type
        self.effects = effects

    def normalize_volume(self, peak: float):
        pass

    def normalize_pitch(self, freq: float):
        pass

    def normalize(self, peak, freq):
        self.normalize_volume(peak)
        self.normalize_pitch(freq)

    def play(self, note: Note) -> Event:
        return self.event
