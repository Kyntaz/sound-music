from SoundMusic.Music import Line, Note
import math

class MotifComposer:
    def compose(self, features: list, instruments: list) -> list:
        l = Line()
        for m in features["scale"]:
            #f = 2**((m-69)/12)*440
            n = Note(60+m, 1, 0.5)
            l.add_notes([n])
        return [l]
