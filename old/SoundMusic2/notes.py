# Simpler midi representation for use with midi generators.
import os
import music21 as m21

class MNote:
    def __init__(self, pitch, dur):
        self.pitch = pitch
        self.dur = dur
        self.t = 0

class MLine:
    def __init__(self):
        self.notes = []
        self.generator = None
        self.name = "Unknown"
    
    def add_note(self, note, t):
        note.t = t
        self.notes.append(note)

# Read midi dataset:
_midis = {}

def init_midis():
    global _midis
    midis_path = "midi/"
    for file in os.listdir(midis_path):
        name = os.path.splitext(file)[0]
        _midis[name] = midis_path + file

def read_midi(name):
    global _midis
    midi = _midis[name]
    return import_midi(midi)

def get_midis():
    global _midis
    return _midis

# Parse midis into our representation:
def score2lines(score: m21.stream.Score):
    lines = []
    for part in score.parts:
        line = MLine()
        line.name = part.partName
        for props in part.flat.toSoundingPitch().secondsMap:
            element = props['element']
            if isinstance(element, m21.chord.Chord):
                # Add a chord
                duration = props['durationSeconds']
                duration = max(duration, 0.01)
                offset = props['offsetSeconds']
                notes = [MNote(p.midi, duration) for p in element.pitches]
                for note in notes: line.add_note(note, offset)
            elif isinstance(element, m21.note.Note):
                # Add a note
                duration = props['durationSeconds']
                duration = max(duration, 0.01)
                offset = props['offsetSeconds']
                pitch = element.pitch.midi
                line.add_note(MNote(pitch, duration), offset)
        lines.append(line)
    return lines

def import_midi(file):
    score = m21.converter.parse(file)
    # Fix Metronome Marks, cause music21 sucks...
    for _,_,t in score.parts[0].metronomeMarkBoundaries():
        for part in score.parts[1:]:
            part.insert(t)
    return score2lines(score)