from SoundMusic.Music import Note
from SoundMusic.EventExtraction import Event
from SoundMusic.Architecture import SYSTEM
from SoundMusic.utils import Envelope as envl
import numpy as np
from pysndfx import AudioEffectsChain as Fx
import librosa as lr
from math import sin, pi, floor
import random

class IInstrument:
    def add_event(self, event: Event): raise NotImplementedError()
    def play(self, note: Note, smpRt: int): raise NotImplementedError()

@SYSTEM.is_instrument
class SampleInstrument(IInstrument):
    def __init__(self):
        self.event_map = {}

    def add_event(self, event: Event):
        self.event_map[event.get_pitch()] = event

    def get_event(self, pitch):
        if pitch in self.event_map:
            return (self.event_map[pitch], pitch)
        else:
            c_pitch = min(self.event_map.keys(), key=lambda k: abs(k-pitch))
            return (self.event_map[c_pitch], c_pitch)

    def play(self, note: Note, smpRt: int) -> np.ndarray:
        event, c_pitch = self.get_event(note.pitch)
        ratio = (len(event.data) / smpRt) / note.duration
        ratio = np.clip(ratio, 0.5, 100)
        shift = note.pitch - c_pitch
        wave = lr.effects.harmonic(event.data)
        wave = (
            Fx()
            .highpass(100)
            .pitch(shift * 100)
            .tempo(ratio)
        )(wave)
        wave = envl.apply(wave, envl.adsr(len(wave)))
        pad = [0] * round(note.start*smpRt)
        wave = np.concatenate((np.array(pad), wave), axis=0)
        return wave

@SYSTEM.is_instrument
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
