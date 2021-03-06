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
import fluidsynth as fl
import processing
import smutils

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
            n = self.n_notes
            sort = np.argsort(profile)[-n:]
            freqs = [fs[i] for i in sort]
            amps = [profile[i] for i in sort]
            phs = [phases[i] for i in sort]
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
            fade = wavef.Envelope.fade()
            fade_s = fade.sample(0, 1, samples.size)
            samples *= fade_s
            so = sounds.SoundObject(samples, audio.rate, t)
            if so.get_dur() > 0.2:
                lso.append(so)
        return lso

class Melody(IGenerator):
    def __init__(self):
        self.soundfont = "./soundfonts/piano.sf2"
        self.bank = (0, 0)
        self.decay = 1.0
        self.band = (220, 1760)
        self.n_notes = 1
        self.amp = 1
        self.scale_complexity = 12

    def get_parameters(self):
        return {
            "font": self.soundfont,
            "bank": self.bank,
            "decay": self.decay,
            "band": self.band,
            "notes": self.n_notes,
            "amp": self.amp,
            "complexity": self.scale_complexity
        }

    def set_parameters(self, params):
        self.soundfont = params["font"]
        self.bank = params["bank"]
        self.decay = params["decay"]
        self.band = params["band"]
        self.n_notes = params["notes"]
        self.amp = params["amp"]
        self.scale_complexity = params["complexity"]

    def generate_note(self, synth, pitch, dur, rate):
        synth.noteon(0, int(pitch), 100)
        samps = synth.get_samples(int(dur*44100))
        synth.noteoff(0, int(pitch))
        samps = np.append(samps, synth.get_samples(int(44100*self.decay)))
        samps = samps[::2]
        samps = lr.resample(samps.astype(float), 44100, rate)
        return (samps / 10000) * self.amp

    def generate(self, audio):
        audio = copy.deepcopy(audio)
        lso = []
        pitches, mags = lr.piptrack(
            audio.samples, audio.rate,
            fmin=self.band[0], fmax=self.band[1]
        )
        chroma = np.mean(lr.feature.chroma_stft(audio.samples, audio.rate), axis=1)
        n = self.scale_complexity
        notes = np.argsort(chroma)[-n:]
        onsets = lr.onset.onset_detect(
            audio.samples, audio.rate,
            units='frames'
        )
        synth = fl.Synth()
        sfid = synth.sfload(self.soundfont)
        synth.program_select(0, sfid, self.bank[0], self.bank[1])
        for onset,o2 in zip(onsets, onsets[1:]):
            time = lr.frames_to_time(onset, audio.rate)
            profile = mags[:,onset]
            n = self.n_notes
            sort = np.argsort(profile)[-n:]
            freqs = [pitches[i,onset] for i in sort if pitches[i,onset] > 0]
            dur = lr.frames_to_time(o2, audio.rate) - lr.frames_to_time(onset, audio.rate)
            for f in freqs:
                note = round(lr.hz_to_midi(f))
                note = smutils.find_nearest(notes, note % 12) + ((note // 12) * 12)
                samps = self.generate_note(synth, note, dur, audio.rate)
                so = sounds.SoundObject(samps, audio.rate, time)
                lso.append(so)
        return lso

class Harmony(IGenerator):
    def __init__(self):
        self.soundfont = "./soundfonts/piano.sf2"
        self.bank = (0,0)
        self.n_notes = 3
        self.octaves = [3,4]
        self.decay = 1.0
        self.amp = 1.0
        self.min_max_bar = (3,12)
    
    def get_parameters(self):
        return {
            "font": self.soundfont,
            "bank": self.bank,
            "notes": self.n_notes,
            "octaves": self.octaves,
            "decay": self.decay,
            "amp": self.amp,
            "bar_lens": self.min_max_bar
        }

    def set_parameters(self, params):
        self.soundfont = params["font"]
        self.bank = params["bank"]
        self.n_notes = params["notes"]
        self.octaves = params["octaves"]
        self.decay = params["decay"]
        self.amp = params["amp"]
        self.min_max_bar = params["bar_lens"]

    def generate_note(self, synth, pitch, dur, rate):
        synth.noteon(0, int(pitch), 100)
        samps = synth.get_samples(int(dur*44100))
        synth.noteoff(0, int(pitch))
        samps = np.append(samps, synth.get_samples(int(44100*self.decay)))
        samps = samps[::2]
        samps = lr.resample(samps.astype(float), 44100, rate)
        return (samps / 10000) * self.amp
    
    def generate(self, audio):
        audio = copy.deepcopy(audio)
        lso = []
        dbSpect = lr.amplitude_to_db(np.abs(lr.stft(audio.samples)))
        chromagram = lr.feature.chroma_stft(audio.samples, audio.rate)
        _,beats = lr.beat.beat_track(audio.samples, audio.rate)
        dbSpect = lr.util.sync(dbSpect, beats)
        recurrence = lr.segment.recurrence_matrix(dbSpect, sym=True, mode="distance")
        candidates = list(range(self.min_max_bar[0], self.min_max_bar[1]+1))
        scores = processing.get_time_signature(recurrence, candidates)
        ts = candidates[np.argmax(scores)]
        measure_bars = beats[::ts]
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        synth = fl.Synth()
        sfid = synth.sfload(self.soundfont)
        synth.program_select(0, sfid, self.bank[0], self.bank[1])
        for mb,mb2 in zip(measure_bars, measure_bars[1:]):
            profile = np.mean(chromagram[:, mb:mb2], axis=1)
            dur = lr.frames_to_time(mb2, audio.rate) - lr.frames_to_time(mb, audio.rate)
            n = self.n_notes
            sort = np.argsort(profile)[-n:]
            to_render = [notes[i] + str(random.choice(self.octaves)) \
                for i in sort]
            t = lr.frames_to_time(mb, audio.rate)
            for note in to_render:
                midi = lr.note_to_midi(note)
                samps = self.generate_note(synth, midi, dur, audio.rate)
                so = sounds.SoundObject(samps, audio.rate, t)
                lso.append(so)
        return lso

# Mapping from generator classes to their name in the repl:
_generators = {
    "ghosts": GhostsGenerator,
    "440": Test440,
    "id": Identity,
    "events": Events,
    "melody": Melody,
    "harmony": Harmony,
}

def get_generator(id):
    global _generators
    return _generators[id]

def get_generators():
    global _generators
    return _generators