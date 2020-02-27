from SoundMusic.Music import Piece, Line
import copy

class Arranger:
    def arrange(self, instruments: list, features, motifs) -> list:
        c = 0
        p = Piece()
        for instrument in instruments:
            for motif in motifs:
                line = Line()
                line.set_cursor(c)
                for note in motif.notes:
                    line.add_notes([copy.deepcopy(note)])
                p.add_line(line, instrument)
                c = line.cursor
        return [p]