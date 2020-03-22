from SoundMusic.Music import Note
from SoundMusic.EventExtraction import Event
from SoundMusic.utils import Envelope as envl
import numpy as np
from pysndfx import AudioEffectsChain as Fx
import librosa as lr
import math
from math import sin, pi, floor, ceil
from SoundMusic.utils.Random import maybe
import random
from SoundMusic.utils.Wave import get_strong_freq, stitch_nwaves

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
        wave = envl.adsr(len(wave))(wave)
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
        if maybe(0.5): self.sample = event.data

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
        wave = envl.adsr(len(wave))(wave)
        return wave

class Granulator(IInstrument):
    def __init__(self):
        self.grans = []
        self.size = 300
        self.smoothing = 10
        self.limit = 100
        self.break_limit = 5
        self.gran_len = self.size + self.smoothing
        self.cached_range = None

    def add_event(self, event):
        n_grans = len(event.data) / self.gran_len
        grans = np.array_split(event.data, n_grans)
        self.grans += grans

    def gen_wave(self, dur, smpRt):
        n_grans = ceil(math.floor(dur * smpRt / self.size))
        grans = random.choices(self.grans, k=n_grans)
        random.shuffle(grans)
        return stitch_nwaves(grans, self.smoothing)
        
    def play(self, note: Note, smpRt):
        wave = None
        shift = math.inf
        for _ in range(self.limit):
            twave = self.gen_wave(note.duration, smpRt)
            tc_pitch = get_strong_freq(twave)
            if tc_pitch == - math.inf: continue
            tshift = note.pitch - tc_pitch
            if abs(tshift) < abs(shift):
                wave = twave
                shift = tshift
            if abs(shift) < 30: break
        wave = (
            Fx()
            .pitch(shift * 100)
            .highpass(lr.midi_to_hz(note.pitch))
        )(wave)
        wave = envl.adsr(len(wave))(wave)
        return wave

    def range(self):
        if self.cached_range == None:
            s = math.inf
            b = 0
            r = 0
            for _ in range(self.limit):
                p = get_strong_freq(self.gen_wave(random.uniform(0.5, 1), 22050))
                if p == - math.inf: continue
                if s < p < b: r += 1
                if r > self.break_limit: break
                s = min(s, p)
                b = max(b, p)
            self.cached_range = (s,b)
        return self.cached_range

all_instruments = [
    MelodicSample,
    Oscillator,
    Granulator,
]