from EventExtraction import Event


class InstrumentGenerator:
    def __init__(self, instrument_classes: list=[]):
        self.instrument_classes = instrument_classes
        self.instruments = []

    def add_instrument_class(self, instrument):
        self.instrument_classes.append(instrument)

    def generate(self, events: Event):
        pass

    def is_instrument(self, cl):
        self.add_instrument_class(cl)
        return cl