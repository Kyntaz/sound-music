from SoundMusic.Music import Piece
from SoundMusic.Audio import Audio
import numpy as np
import librosa as lr
import soundfile as sf
import warnings

class AudioRenderer:
    def render(self, piece: Piece, smpRt: int, out: str):
        wave = np.array([])
        for line in piece.lines:
            for note in line.notes:
                try:
                    rNote = line.instrument.play(note, smpRt)
                    if len(wave) < len(rNote):
                        wave = np.concatenate((wave, [0]*(len(rNote) - len(wave))))
                    elif len(wave) > len(rNote):
                        rNote = np.concatenate((rNote, [0]*(len(wave) - len(rNote))))
                    wave += rNote
                except: warnings.warn("Could not render a note.")
        assert len(wave) > 0
        sf.write(out, wave, smpRt, subtype='PCM_24')
        return Audio(wave, smpRt)
