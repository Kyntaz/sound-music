import librosa as lr
import numpy as np
from matplotlib import pyplot as plt
import SoundMusic as sm
from SoundMusic import SoundObject
from SoundMusic.mustruct import Note

MAX_SAMPLES = 3

class Sampler3:
    def __init__(self, lso):
        self.sounds = []
        for so in lso:
            ptrack, mtrack = so.track_pitch()
            pitch = np.mean(ptrack)
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
        
        pitch,_ = SoundObject(out).track_pitch()
        pitch = np.mean(pitch)
        if pitch > 0:
            out = lr.effects.pitch_shift(
                out, sm.sound.SAMPLE_RATE,
                lr.hz_to_midi(note.pitch) - lr.hz_to_midi(pitch)
            )
        
        oso = sm.effects.band_pass(SoundObject(out), note.pitch, 20000)
        return oso

def make_samplers(sampler_class, synths, lso):
    samplers = [sampler_class(lso)]
    for synth in synths:
        nlso = [synth.gen(so) for so in lso]
        samplers.append(sampler_class(nlso))
    return samplers
