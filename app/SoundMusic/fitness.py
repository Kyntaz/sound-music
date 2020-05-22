import SoundMusic as sm
import numpy as np
import librosa as lr

def similarity(sound, source):
    spect1 = lr.amplitude_to_db(np.abs(lr.stft(sound.samples)))
    spect2 = lr.amplitude_to_db(np.abs(lr.stft(source.samples)))
    spect2.resize(spect1.shape)
    spect1 /= np.max(np.abs(spect1))
    spect2 /= np.max(np.abs(spect2))
    diff = np.abs(spect1 - spect2)
    return 1.0 - np.mean(diff)

def amplitude_range(sound):
    spect = lr.amplitude_to_db(np.abs(lr.stft(sound.samples)))
    spect -= np.min(spect)
    agl = np.sum(spect, axis=0)
    agl /= np.max(agl)
    return np.max(agl) - np.min(agl)

def frequency_range(sound):
    pitches, magnitudes = lr.piptrack(sound.samples, sound.rate)
    pitch_track = np.array([pitches[np.argmax(magnitudes[:, t]), t] for t in range(np.shape(pitches)[1])])
    pitch_track /= np.max(lr.fft_frequencies(sound.rate))
    return np.max(pitch_track) - np.min(pitch_track)

def duration(sound, expected):
    return 0.0

def silence_ratio(sound, expected):
    return 0.0