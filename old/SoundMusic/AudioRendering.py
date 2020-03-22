from SoundMusic.Music import Piece
from SoundMusic.Audio import Audio
import numpy as np
import librosa as lr
import soundfile as sf
from pysndfx import AudioEffectsChain as Fx
import warnings
import traceback
import SoundMusic.utils.Exceptions as exceptions
from SoundMusic.utils.Wave import join_waves

class AudioRenderer:
    def render(self, piece: Piece, smpRt: int, out: str):
        wave = np.array([])
        for j,line in enumerate(piece.lines):
            line_wave = np.array([])
            for i,note in enumerate(line.notes):
                print(f"Rendering line {j+1} of {len(piece.lines)}. Rendering at {round((i+1) / len(line.notes) * 100, 2)}% ({exceptions.n_exceptions()} exceptions)     ", end='\r')
                try:
                    pad = pad = [0] * round(note.start*smpRt)
                    note_wave = line.instrument.play(note, smpRt)
                    note_wave = np.concatenate((pad, note_wave))
                    line_wave = join_waves(line_wave, note_wave)
                except Exception as e:
                    #traceback.print_exc()
                    exceptions.save_exception(e)
            wave = join_waves(wave, line_wave)
        assert len(wave) > 0
        wave = (
            Fx()
            .normalize()
            .reverb()
        )(wave)
        sf.write(out, wave, smpRt, subtype='PCM_24')
        print("\nDone Rendering.")
        return Audio(wave, smpRt)
