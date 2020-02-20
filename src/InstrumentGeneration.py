from EventExtraction import Event
import random


class InstrumentGenerator:
    def __init__(self, instrument_classes: list=[]):
        self.instrument_classes = instrument_classes
        self.instruments = []

    def add_instrument_class(self, instrument):
        self.instrument_classes.append(instrument)

    def generate(self, event: Event):
        return random.choice(self.instrument_classes)(event)

    def is_instrument(self, cl):
        self.add_instrument_class(cl)
        return cl