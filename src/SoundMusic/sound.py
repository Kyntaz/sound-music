from typing import List
import librosa as lr
import numpy as np
import sounddevice as sd
import soundfile as sf
from matplotlib import pyplot as plt

import SoundMusic as sm

SAMPLE_RATE = 22100

class SoundObject:
    def __init__(self, samples, t=0, *, normalize=True):
        assert len(samples) > 0.1 * SAMPLE_RATE
        self.samples = np.asfortranarray(samples)
        self.t = 0
        if normalize: self.normalize()

    def play(self):
        sd.play(self.no_click(), samplerate=SAMPLE_RATE)

    @property
    def duration(self):
        return self.samples.size / SAMPLE_RATE

    @property
    def end(self):
        return self.t + self.duration
    
    def write(self, path):
        sf.write(path, self.samples, SAMPLE_RATE)

    def normalize(self):
        peak = np.max(np.abs(self.samples))
        if peak > 1.0:
            self.samples /= peak
    
    def no_click(self):
        f = int(0.05 * SAMPLE_RATE)
        l = self.samples.size
        return np.concatenate([
            np.linspace(0, 1, f),
            np.ones(l - 2 * f),
            np.linspace(1, 0, f)
        ]) * self.samples

    def graph(self, dur=1.0):
        l = int(dur * SAMPLE_RATE)
        plt.plot(self.samples[:l])

    def track_pitch(self):
        pt, mt = lr.piptrack(self.samples, SAMPLE_RATE)
        pitch = [pt[np.argmax(mt[:, t]), t] for t in range(np.shape(pt)[1])]
        mag = np.max(mt, axis=1)
        return np.array(pitch), mag

    def get_f0(self):
        f0 = lr.yin(self.samples, 65, 2093, SAMPLE_RATE)
        return np.mean(f0)

    def get_normalize_to(self, peak):
        og_peak = np.max(np.abs(self.samples))
        if og_peak <= 0: return self
        return SoundObject(self.samples * peak / og_peak)

    def get_padded(self, dur):
        target_samps = int(round(dur * SAMPLE_RATE))
        missing_samps = target_samps - self.samples.size
        if missing_samps <= 0:
            return self.samples[:target_samps]
        return np.concatenate([
            self.samples,
            np.zeros(missing_samps)
        ])

def load(path):
    samples, _ = lr.load(path, sr=SAMPLE_RATE)
    return SoundObject(samples)

def stop():
    sd.stop()

def join(lso: List[SoundObject]):
    dur = int(np.ceil(max([so.end for so in lso]) * SAMPLE_RATE))
    canvas = np.zeros(dur)
    for so in lso:
        samps = so.no_click()
        st = lr.time_to_samples(so.t, SAMPLE_RATE)
        et = st + samps.size
        canvas[st:et] += samps
    return SoundObject(canvas)

def write_stereo(so1: SoundObject, so2: SoundObject, width, path):
    samps = np.stack([
        so1.samples * width - so2.samples * (1.0 - width),
        so2.samples * width - so1.samples * (1.0 - width)
    ], axis=-1)
    sf.write(path, samps, SAMPLE_RATE)
