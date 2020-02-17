class Note:
    def __init__(self, pitch_or_command, duration, intensity):
        if isinstance(pitch_or_command, str):
            self.command = pitch_or_command
            self.pitch = 0
        else:
            self.command = ""
            self.pitch = pitch_or_command
        self.start = 0
        self.duration = duration
        self.intensity = intensity

class Line:
    def __init__(self):
        self.instrument = None
        self.notes = []
        self.cursor = 0
    
    def set_cursor(self, cursor):
        self.cursor = cursor

    def add_notes(self, notes):
        for note in notes:
            note.start = self.cursor
        self.notes += notes
        self.cursor += max([note.duration for note in notes])

class Piece:
    def __init__(self):
        self.lines = []
    
    def add_line(self, line, instrument):
        line.instrument = instrument
        self.lines += [line]