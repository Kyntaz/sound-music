import numpy as np
import librosa as lr
import SoundMusic as sm
from SoundMusic.compact_manipulators.base import  ISimpleManipulator
from SoundMusic.sound import SoundObject
import math
import scipy as sp
import random

def _sine(t, f, a, ph):
    return math.sin(t * 2 * math.pi * f + ph) * a

def _square(t, f, a, ph):
    return np.sign(math.sin(t * 2 * math.pi * f + ph)) * a

_vsine = np.vectorize(_sine)
_vsquare = np.vectorize(_square)

class Modulate(ISimpleManipulator):

    def __init__(self):
        self.shape = 0

        self.shapes = [_vsine, _vsquare]

    def tweak(self, power):
        self.shape = random.choice([0, 1])

    def do(self, sound):
        lso = []
        pitches, magnitudes = lr.piptrack(sound.samples, sound.rate)
        pitch_track = [pitches[np.argmax(magnitudes[:, t]), t] for t in range(np.shape(pitches)[1])]
        mag_track = [magnitudes[np.argmax(magnitudes[:, t]), t] for t in range(np.shape(pitches)[1])]
        times = np.linspace(sound.t, sound.end(), sound.samples.size)
        times_f = lr.time_to_frames(times, sound.rate)
        pitch_track = [pitch_track[t] for t in times_f if 0 <= t < len(pitch_track)]
        mag_track = [mag_track[t] for t in times_f if 0 <= t < len(mag_track)]
        wave = self.shapes[self.shape](times, pitch_track, mag_track, 0)
        nso = SoundObject(wave, sound.rate, sound.t)
        lso.append(nso)
        return sm.render.render_audio(lso)

class WaveMod(ISimpleManipulator):

    def __init__(self):
        self.base = 440
        self.shape = 0

        self.shapes = [_vsine, _vsquare]

    def tweak(self, power):
        self.shape = random.choice([0, 1])
        
    def do(self, sound):
        lso = []
        contour = sound.samples
        contour_p = np.clip(contour + self.base, 1, None)
        contour_a = np.abs(contour)
        times = np.linspace(sound.t, sound.end(), sound.samples.size)
        wave = self.shapes[self.shape](times, contour_p, contour_a, 0)
        nso = SoundObject(wave, sound.rate, sound.t)
        lso.append(nso)
        return sm.render.render_audio(lso)