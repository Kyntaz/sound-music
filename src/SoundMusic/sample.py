import librosa as lr
import numpy as np
from matplotlib import pyplot as plt
import SoundMusic as sm
from SoundMusic import SoundObject
from SoundMusic.mustruct import Note
from SoundMusic.synth import get_features
import sklearn as skl
import os

MAX_SAMPLES = 3
N_SAMPLERS = 5

class Sampler3:
    def __init__(self, lso):
        self.sounds = []
        for so in lso:
            _, mtrack = so.track_pitch()
            pitch = so.get_f0()
            mag = np.mean(mtrack)
            dur = so.duration
            self.sounds.append((so, pitch, mag, dur))

    def play(self, npitch, nmag, ndur):
        note = Note(npitch, nmag, ndur)

        if note.pitch <= 0:
            samps = np.zeros(int(note.dur * sm.sound.SAMPLE_RATE))
            return SoundObject(samps)

        n_samples = int(note.dur * sm.sound.SAMPLE_RATE)
        factors = []
        for so,pitch,mag,dur in self.sounds:
            p_dif = (note.pitch - pitch) ** 2
            m_dif = (note.mag - mag) ** 2
            d_dif = (note.dur - dur) ** 2
            wei = 1 / np.sqrt(p_dif + m_dif + d_dif)
            samps = so.samples
            if samps.size > n_samples:
                samps = samps[:n_samples]
            elif samps.size < n_samples:
                samps = np.concatenate([samps, np.zeros(n_samples - samps.size)])
            factors.append([samps, wei])
        
        total = sum([w for _,w in factors])
        factors = sorted(factors, key=lambda fac: fac[1])[-MAX_SAMPLES:]
        out = np.zeros(n_samples)
        for samps, wei in factors:
            out += samps * wei / total
        
        pitch = SoundObject(out).get_f0()
        if pitch > 0:
            out = lr.effects.pitch_shift(
                out, sm.sound.SAMPLE_RATE,
                lr.hz_to_midi(note.pitch) - lr.hz_to_midi(pitch)
            )
        
        oso = sm.effects.band_pass(SoundObject(out), note.pitch, 20000)
        return oso

    def save(self, out):
        out_txt = ""
        i = 0
        for so, fr, mag, _ in self.sounds:
            pitch = lr.hz_to_midi(fr)
            vel = np.clip(mag * 127, 0, 127)
            path = os.path.dirname(out)
            fname = os.path.splitext(os.path.basename(out))[0] + f"_s{i}.wav"
            so.write(os.path.join(path, fname))
            out_txt += f"{fname}, {pitch}, {vel}\n"
            i += 1

        with open(out, "w") as file:
            file.write(out_txt)

def make_samplers(sampler_class, synths, lso, save=False, op="", n_samplers=N_SAMPLERS):
    nlso = [[synth.gen(so) for so in lso] for synth in synths]

    if save:
        for i,so in enumerate([item for l in nlso for item in l]):
            so.write(f"{op}/snd_{i}.wav")

    return [sampler_class(sounds) for sounds in nlso]
