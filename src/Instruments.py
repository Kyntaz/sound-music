from Music import Note
from EventExtraction import Event
from Architecture import SYSTEM
import numpy as np
from pysndfx import AudioEffectsChain
import librosa as lr

@SYSTEM.is_instrument
class Instrument:
    def __init__(self, event: Event, effects: list=[]):
        self.event = event
        self.pitch = event.get_pitch()
        self.type = event.type
        self.effects = effects

    def play(self, note: Note, smpRt: int) -> np.ndarray:
        pad = [0] * (note.start*smpRt)
        wave = np.concatenate((np.array(pad), self.event.data), axis=0)
        wave = lr.effects.harmonic(wave)
        shift = note.pitch - self.pitch
        wave = (
            AudioEffectsChain()
            .pitch(shift * 100)
        )(wave)
        return wave
