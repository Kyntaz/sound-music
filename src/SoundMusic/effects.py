import SoundMusic as sm
from SoundMusic import SoundObject
import scipy as sp
import numpy as np
import librosa as lr

def band_pass(so: SoundObject, low, high, order=5):
    nyq = 0.5 * sm.sound.SAMPLE_RATE
    low = np.clip(low / nyq, 0.001, 0.999)
    high = np.clip(high / nyq, 0.001, 0.999)
    b, a = sp.signal.butter(order, [low, high], btype="band")
    out = sp.signal.lfilter(b, a, so.samples)
    return SoundObject(np.nan_to_num(out))

def get_room(so: SoundObject, dur):
    dur_samps = lr.time_to_samples(dur, sm.sound.SAMPLE_RATE)
    room = np.zeros(dur_samps, dtype=so.samples.dtype)
    silences = lr.onset.onset_detect(so.samples, sm.sound.SAMPLE_RATE,
        wait=int(dur_samps / 512), units="samples")
    count = 0
    for e,e2 in zip(silences, silences[1:]):
        ss = int(e + 0.01 * sm.sound.SAMPLE_RATE)
        es = int(min(ss + dur_samps, max(e2 - 0.01 * sm.sound.SAMPLE_RATE, 0)))
        if es < so.samples.size and es - ss > 0.1 * sm.sound.SAMPLE_RATE:
            response = so.samples[ss:es]
            room += SoundObject(response).get_padded(dur)
            count += 1
    if count == 0: return None
    room /= count
    room *= np.linspace(1, 0.0,  dur_samps)
    return SoundObject(room)

def reverberate(room: SoundObject, so: SoundObject):
    samps = np.convolve(so.samples, room.samples, mode='same')
    return SoundObject(samps)