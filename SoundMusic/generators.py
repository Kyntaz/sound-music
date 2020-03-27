# Music generators that take a sound chunk and produce sound objects from it.
import wavef
import sounds
import librosa as lr
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import copy
from pysndfx import AudioEffectsChain as Fx
import cmath as cmt
import random

class IGenerator:
    def get_parameters(self): return None
    def set_parameters(self, params): pass
    def generate(self, audio): raise NotImplementedError

class GhostsGenerator(IGenerator):
    def __init__(self):
        self.adsr = wavef.Envelope.adsr()
        self.amp = 0.5
        self.n_notes = 3
        self.band = (100, 2000)
        self.dur = 1

    def get_parameters(self):
        return {
            "attack": (0.2, 1),
            "decay": (0.1, 1),
            "sustain": (0.5, 1),
            "release": (0.2, 0),
            "amplitude": self.amp,
            "notes": self.n_notes,
            "band": self.band,
            "duration": self.dur,
        }

    def set_parameters(self, params):
        self.adsr = wavef.Envelope.adsr(
            a=params["attack"],
            d=params["decay"],
            s=params["sustain"],
            r=params["release"]
        )
        self.amp = params["amplitude"]
        self.n_notes = params["notes"]
        self.band  = params["band"]
        self.dur = params["duration"]

    def generate(self, audio):
        audio = copy.deepcopy(audio)
        audio.samples = (
            Fx()
            .highpass(self.band[0])
            .lowpass(self.band[1])
        )(audio.samples)
        lso = []
        fft = lr.stft(audio.samples)
        fft_a = np.abs(fft)
        fft_a /= fft_a.max()
        fft_ph = np.angle(fft)
        fs = lr.fft_frequencies(audio.rate)
        onsets = lr.onset.onset_detect(
            audio.samples, audio.rate,
            units='frames'
        )
        for onset in onsets:
            time = lr.frames_to_time(onset, audio.rate)
            profile = fft_a[:,onset]
            phases = fft_ph[:,onset]
            sort = np.argsort(profile)
            s = sort.size - 1
            sort = np.array(list(map(lambda x: s - x, sort)))
            freqs = [fs[i] for i in range(len(sort)) \
                if sort[i] < self.n_notes]
            amps = [profile[i] for i in range(len(sort)) \
                if sort[i] < self.n_notes]
            phs = [phases[i] for i in range(len(sort)) \
                if sort[i] < self.n_notes]
            for f,a,ph in zip(freqs, amps, phs):
                wave = wavef.WaveFunction.sine(f, a*self.amp, ph)
                wave_s = wave.sample(0, self.dur, round(audio.rate * self.dur))
                env_s = self.adsr.sample(0, 1, round(audio.rate * self.dur))
                so = sounds.SoundObject(wave_s*env_s, audio.rate, time)
                lso.append(so)
        return lso

class Test440(IGenerator):
    def generate(self, audio):
        wave = wavef.WaveFunction.sine(440, 0.2, 0)
        wave_s = wave.sample(0, 5, audio.rate * 5)
        so = sounds.SoundObject(wave_s, audio.rate, 0)
        return [so]

class Identity(IGenerator):
    def generate(self, audio):
        audio = copy.deepcopy(audio)
        so = sounds.SoundObject(audio.samples, audio.rate, 0)
        return [so]

class Events(IGenerator):
    def __init__(self):
        self.min_len = 0.2
        self.rvar = 5
    
    def get_parameters(self):
        return {
            "minimum_len": self.min_len,
            "random_var": self.rvar,
        }

    def set_parameters(self, params):
        self.min_len = params["minimum_len"]
        self.rvar = params["random_var"]

    def generate(self, audio):
        audio = copy.deepcopy(audio)
        lso = []
        onsets = lr.onset.onset_detect(
            audio.samples, audio.rate,
            units="samples",
            backtrack=True
        )
        for o1,o2 in zip(onsets, onsets[1:]):
            samples = audio.samples[o1:o2]
            t = lr.samples_to_time(o1, audio.rate) + random.uniform(-5, 5)
            t = max(0, t)
            so = sounds.SoundObject(samples, audio.rate, t)
            if so.get_dur() > 0.2:
                lso.append(so)
        return lso

# Mapping from generator classes to their name in the repl:
_generators = {
    "ghosts": GhostsGenerator,
    "440": Test440,
    "id": Identity,
    "events": Events,
}

def get_generator(id):
    global _generators
    return _generators[id]

def get_generators():
    global _generators
    return _generators