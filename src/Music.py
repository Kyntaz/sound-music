class Note:
    def __init__(self, pitch: float, duration: float, intensity: float, meta: dict):
        self.pitch = pitch
        self.start = 0
        self.duration = duration
        self.intensity = intensity
        self.meta = meta

class Line:
    def __init__(self):
        self.instrument = None
        self.notes = []
        self.cursor = 0
    
    def set_cursor(self, cursor):
        self.cursor = cursor

    def add_notes(self, notes: list):
        for note in notes:
            note.start = self.cursor
        self.notes += notes
        self.cursor += max([note.duration for note in notes])

class Piece:
    def __init__(self):
        self.lines = []
    
    def add_line(self, line: Line, instrument):
        line.instrument = instrument
        self.lines += [line]