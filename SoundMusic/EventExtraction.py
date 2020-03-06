from SoundMusic.Audio import Audio
import numpy as np
import librosa as lr
import random
import SoundMusic.utils.Stats as stats
from SoundMusic.utils.Wave import get_strong_freq
from pysndfx import AudioEffectsChain as Fx

class Event:
    def __init__(self, data: np.array):
        self.data = data
        self.type = ""

    def get_pitch(self):
        return get_strong_freq(self.data)
    
    def get_purity(self):
        spect = lr.amplitude_to_db(np.abs(lr.stft(self.data)))
        profile = np.mean(spect, axis=1)
        bins = lr.fft_frequencies()
        return stats.std(bins, profile)

class EventExtractor:
    def extract(self, audio: Audio) -> list:
        onsets = lr.onset.onset_detect(audio.data, backtrack=True, units="samples")
        events = []
        self.val_add(events, audio.data[0:onsets[0]], audio.smpRt)
        for i in range(len(onsets) - 1):
            self.val_add(events, audio.data[onsets[i]:onsets[i+1]], audio.smpRt)
        self.val_add(events, audio.data[onsets[-1]:-1], audio.smpRt)
        for event in events: self.classify(event)
        return events

    def val_add(self, events, data, smpRt):
        if len(data) / smpRt >= 0.2: events.append(Event(data))

    def classify(self, event: Event):
        purity = event.get_purity()
        if purity < 3100:
            event.type = "melodic"
        elif purity < 3200:
            event.type = "textural"
        else:
            event.type = "percussive"