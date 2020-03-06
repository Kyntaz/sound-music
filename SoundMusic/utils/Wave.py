import numpy as np
import librosa as lr
import SoundMusic.utils.Stats as stats
from pysndfx import AudioEffectsChain as Fx

def get_strong_freq(wave):
    pwave = (
        Fx()
        .highpass(100)
    )(wave)
    spect = lr.amplitude_to_db(np.abs(lr.stft(pwave)))
    profile = np.mean(spect, axis=1)
    bins = lr.fft_frequencies()
    return round(lr.hz_to_midi(stats.mode(bins, profile)), 2)

def join_waves(a1, a2):
    if len(a1) < len(a2):
        a1 = np.concatenate((a1, [0]*(len(a2) - len(a1))))
    elif len(a1) > len(a2):
        a2 = np.concatenate((a2, [0]*(len(a1) - len(a2))))
    return a1 + a2

def stitch_nwaves(waves, smoothing):
    out = np.array([])
    for w in waves:
        if len(out) > 0: pad = [0]*(len(out) - smoothing)
        else: pad = []
        s1 = np.concatenate([
            np.array([1] * (len(out) - smoothing)),
            np.linspace(1, 0, smoothing)
        ])
        s2 = np.concatenate([
            np.linspace(0, 1, smoothing),
            np.array([1] * (len(w) - smoothing))
        ])
        if (len(out)) > 0: out = out * s1
        sw = w * s2
        pw = np.concatenate((pad, sw))
        out = join_waves(out, pw)
    return out