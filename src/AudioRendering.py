from Music import Piece
from Audio import Audio
import numpy as np
import soundfile as sf

class AudioRenderer:
    def render(self, piece: Piece, smpRt: int, out: str):
        wave = np.array([])
        for line in piece.lines:
            for note in line.notes:
                rNote = line.instrument.play(note, smpRt)
                if len(wave) < len(rNote):
                    wave = np.concatenate((wave, [0]*(len(rNote) - len(wave))))
                elif len(wave) > len(rNote):
                    rNote = np.concatenate((rNote, [0]*(len(wave) - len(rNote))))
                wave += rNote
        sf.write(out, wave, smpRt, subtype='PCM_24')
        return Audio(wave, smpRt)
