from SoundMusic.Music import Note
from SoundMusic.EventExtraction import Event
from SoundMusic.utils import Envelope as envl
import numpy as np
from pysndfx import AudioEffectsChain as Fx
import librosa as lr
import math
from math import sin, pi, floor
import random

class IInstrument:
    def add_event(self, event: Event): raise NotImplementedError()
    def play(self, note: Note, smpRt: int): raise NotImplementedError()
    def range(self): return (0, math.inf)

class MelodicSample(IInstrument):
    def __init__(self):
        self.event_map = {}

    def add_event(self, event: Event):
        p = event.get_pitch()
        if not p in self.event_map:
            self.event_map[p] = [event]
        else:
            self.event_map[p] += [event]

    def get_event(self, pitch):
        if pitch in self.event_map:
            return (random.choice(self.event_map[pitch]), pitch)
        else:
            c_pitch = min(self.event_map.keys(), key=lambda k: abs(k-pitch))
            return (random.choice(self.event_map[c_pitch]), c_pitch)

    def play(self, note: Note, smpRt: int) -> np.ndarray:
        event, c_pitch = self.get_event(note.pitch)
        ratio = (len(event.data) / smpRt) / note.duration
        ratio = np.clip(ratio, 0.5, 100)
        shift = note.pitch - c_pitch
        wave = lr.effects.harmonic(event.data)
        wave = (
            Fx()
            .pitch(shift * 100)
            .tempo(ratio)
            .highpass(lr.midi_to_hz(note.pitch))
        )(wave)
        wave = envl.apply(wave, envl.adsr(len(wave)))
        pad = [0] * round(note.start*smpRt)
        wave = np.concatenate((np.array(pad), wave), axis=0)
        return wave

    def range(self):
        s = math.inf
        b = 0
        for p in self.event_map:
            s = min(p, s)
            b = max(p, b)
        return (s,b)

class Oscillator(IInstrument):
    def __init__(self):
        self.sample = None
    
    def add_event(self, event: Event):
        self.sample = event.data

    def play(self, note: Note, smpRt: int):
        b_wave = np.array([])
        freq = lr.midi_to_hz(note.pitch)
        oscs = floor(note.duration * freq)
        for _ in range(oscs):
            l = round(0.005 * smpRt)
            p = random.randint(0, len(self.sample) - l)
            p_wave = self.sample[p:p+l]
            b_wave = np.concatenate((b_wave, p_wave))
        l = round(0.005 * smpRt)
        p = random.randint(0, len(self.sample) - l)
        wave = self.sample[p:p+l]
        wave = np.tile(wave, oscs)
        b_wave = (
            Fx()
            .gain(-10)
        )(b_wave)
        wave = wave + b_wave
        factor = (len(wave) / smpRt) / note.duration
        wave = (
            Fx()
            .speed(factor)
            .highpass(100)
            .lowpass(2000)
        )(wave)
        wave = envl.apply(wave, envl.adsr(len(wave)))
        pad = [0] * round(note.start*smpRt)
        wave = np.concatenate((np.array(pad), wave), axis=0)
        return wave

all_instruments = [
    MelodicSample,
    Oscillator,
]