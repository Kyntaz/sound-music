import numpy as np
import librosa as lr
import SoundMusic as sm
from SoundMusic.manipulators.base import  ISimpleManipulator
from SoundMusic.sound import SoundObject
import math
import scipy as sp
import random

def _sine(t, f, a, ph):
    return math.sin(t * 2 * math.pi * f + ph) * a

_vsine = np.vectorize(_sine)

class Modulate(ISimpleManipulator):

    def __init__(self):
        self.window = 500

    def tweak(self, power):
        self.window += int(round(np.clip(random.uniform(-1,1) * 20000 * power, 1, 20000)))

    def do(self, sounds):
        lso = []
        for so in sounds:
            pitches, magnitudes = lr.piptrack(so.samples, so.rate)
            pitch_track = [pitches[np.argmax(magnitudes[:, t]), t] for t in range(np.shape(pitches)[1])]
            mag_track = [magnitudes[np.argmax(magnitudes[:, t]), t] for t in range(np.shape(pitches)[1])]
            times = np.linspace(so.t, so.end(), so.samples.size)
            times_f = lr.time_to_frames(times, so.rate)
            pitch_track = [pitch_track[t] for t in times_f if 0 <= t < len(pitch_track)]
            mag_track = [mag_track[t] for t in times_f if 0 <= t < len(mag_track)]
            pitch_track = sp.signal.convolve(pitch_track, np.ones(self.window) / self.window, mode='same')
            pitch_track = sp.signal.convolve(pitch_track, np.ones(self.window) / self.window, mode='same')
            wave = _vsine(times, pitch_track, mag_track, 0)
            nso = SoundObject(wave, so.rate, so.t)
            lso.append(nso)
        return lso

class WaveMod(ISimpleManipulator):

    def __init__(self):
        self.window = 500
        self.base = 440

    def tweak(self, power):
        self.window += int(round(np.clip(random.uniform(-1,1) * 20000 * power, 1, 20000)))
        
    def do(self, sounds):
        lso = []
        for so in sounds:
            contour = sp.signal.convolve(so.samples, np.ones(self.window) / self.window, mode='same')
            contour_p = np.clip(contour + self.base, 1, None)
            contour_a = np.abs(contour)
            times = np.linspace(so.t, so.end(), so.samples.size)
            wave = _vsine(times, contour_p, contour_a, 0)
            nso = SoundObject(wave, so.rate, so.t)
            lso.append(nso)
        return lso