from SoundMusic.Music import Note, Line, Piece
import music21 as m21
import warnings

def smpiece2score(piece: Piece):
    raise NotImplementedError

def score2smpiece(score: m21.stream.Score):
    piece = Piece()
    for part in score.parts:
        line = Line()
        for props in part.flat.toSoundingPitch().secondsMap:
            element = props['element']
            if isinstance(element, m21.chord.Chord):
                # Add a chord
                duration = props['durationSeconds']
                duration = max(duration, 0.01)
                offset = props['offsetSeconds']
                line.set_cursor(offset)
                notes = [Note(p.midi, duration, 1.0) for \
                    p in element.pitches]
                line.add_notes(notes)
            elif isinstance(element, m21.note.Note):
                # Add a note
                duration = props['durationSeconds']
                duration = max(duration, 0.01)
                offset = props['offsetSeconds']
                line.set_cursor(offset)
                pitch = element.pitch.midi
                line.add_notes([Note(pitch, duration, 1.0)])
        piece.add_line(line)
    return piece

def read_midi(file):
    score = m21.converter.parse(file)
    # Fix Metronome Marks, cause music21 sucks...
    for _,_,t in score.parts[0].metronomeMarkBoundaries():
        for part in score.parts[1:]:
            part.insert(t)
    return score2smpiece(score)