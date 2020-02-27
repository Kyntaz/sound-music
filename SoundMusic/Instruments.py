from SoundMusic.Music import Note
from SoundMusic.EventExtraction import Event
from SoundMusic.Architecture import SYSTEM
import numpy as np
from pysndfx import AudioEffectsChain
import librosa as lr

@SYSTEM.is_instrument
class Instrument:
    def __init__(self, event: Event=None, effects: list=[]):
        self.event_map = {}
        self.effects = effects

    def add_event(self, event: Event):
        self.event_map[event.get_pitch()] = event

    def get_event(self, pitch):
        if pitch in self.event_map:
            return (self.event_map[pitch], pitch)
        else:
            c_pitch = min(self.event_map.keys(), key=lambda k: abs(k-pitch))
            return (self.event_map[c_pitch], c_pitch)

    def play(self, note: Note, smpRt: int) -> np.ndarray:
        pad = [0] * (note.start*smpRt)
        event, c_pitch = self.get_event(note.pitch)
        wave = np.concatenate((np.array(pad), event.data), axis=0)
        wave = lr.effects.harmonic(wave)
        shift = note.pitch - c_pitch
        wave = (
            AudioEffectsChain()
            .pitch(shift * 100)
        )(wave)
        return wave
