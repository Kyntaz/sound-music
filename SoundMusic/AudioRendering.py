from SoundMusic.Music import Piece
from SoundMusic.Audio import Audio
import numpy as np
import librosa as lr
import soundfile as sf
from pysndfx import AudioEffectsChain as Fx
import warnings
import traceback

class AudioRenderer:
    def render(self, piece: Piece, smpRt: int, out: str):
        wave = np.array([])
        for j,line in enumerate(piece.lines):
            print(f"Rendering line {j+1} of {len(piece.lines)}.")
            for i,note in enumerate(line.notes):
                print(f"Rendering at {round(i / len(line.notes) * 100, 2)}%")
                try:
                    note_wave = line.instrument.play(note, smpRt)
                    wave = _join_arrays(wave, note_wave)
                except:
                    traceback.print_exc()
        assert len(wave) > 0
        wave = (
            Fx()
            .normalize()
            .reverb()
        )(wave)
        sf.write(out, wave, smpRt, subtype='PCM_24')
        return Audio(wave, smpRt)

def _join_arrays(a1: np.ndarray, a2: np.ndarray):
    if len(a1) < len(a2):
        a1 = np.concatenate((a1, [0]*(len(a2) - len(a1))))
    elif len(a1) > len(a2):
        a2 = np.concatenate((a2, [0]*(len(a1) - len(a2))))
    return a1 + a2
