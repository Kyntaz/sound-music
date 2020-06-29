import librosa as lr
import numpy as np
import SoundMusic as sm
from SoundMusic.sound import SoundObject

MIN_DB = 0
MAX_DB = 210
MIN_LEN = 0.5
MAX_LEN = 5.0

def extract(so, min_db, max_db, min_len, max_len):
    # Recursively search for the best threshold.
    samples = so.samples
    sr = sm.sound.SAMPLE_RATE
    if abs(min_db - max_db) < 2.0:
        segments = lr.effects.split(samples, top_db=max_db)
        segments = [(s[0], s[1] - 1) for s in segments if sr * max_len > abs(s[0] - s[1]) > sr * min_len]
        return segments
    
    s1 = lr.effects.split(samples, top_db=(min_db + (max_db - min_db) * (1 / 4)))
    s1 = [(s[0], s[1] - 1) for s in s1 if sr * max_len > abs(s[0] - s[1]) > sr * min_len]
    s2 = lr.effects.split(samples, top_db=(min_db + (max_db - min_db) * (3 / 4)))
    s2 = [(s[0], s[1] - 1) for s in s2 if sr * max_len > abs(s[0] - s[1]) > sr * min_len]
    s3 = lr.effects.split(samples, top_db=(min_db + (max_db - min_db) / 2))
    s3 = [(s[0], s[1] - 1) for s in s3 if sr * max_len > abs(s[0] - s[1]) > sr * min_len]
    
    if len(s3) > len(s1) and len(s3) > len(s2):
        return extract(so, min_db + (max_db - min_db) * (1 / 4),
            min_db + (max_db - min_db) * (3 / 4), min_len, max_len)
    elif len(s1) > len(s2):
        return extract(so, min_db, min_db + (max_db - min_db) / 2, min_len, max_len)
    elif len(s1) < len(s2):
        return extract(so, min_db + (max_db - min_db) / 2, max_db, min_len, max_len)
    else:
        t1 = extract(so, min_db, min_db + (max_db - min_db) / 2,min_len, max_len)
        t2 = extract(so, min_db + (max_db - min_db) / 2, max_db, min_len, max_len)
        if len(t1) >= len(t2):
            return t1
        else:
            return t2

def get_sounds(so, min_db=None, max_db=None, min_len=None, max_len=None):
    global MIN_DB, MAX_DB, MIN_LEN, MAX_LEN
    min_db = min_db or MIN_DB
    max_db = max_db or MAX_DB
    min_len = min_len or MIN_LEN
    max_len = max_len or MAX_LEN
    segments = extract(so, min_db, max_db, min_len, max_len)
    lso = []
    samples = so.samples
    for s in segments:
        segment_samples = samples[s[0]:s[1]]
        nso = SoundObject(segment_samples)
        lso.append(nso)
    return lso
