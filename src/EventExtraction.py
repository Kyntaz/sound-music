from Audio import Audio
import numpy as np
import librosa as lr
import random

class Event:
    def __init__(self, data: np.array):
        self.data = data
        self.type = ""

    def get_pitch(self):
        chroma = lr.cqt(self.data)
        profile = np.mean(chroma, axis=1)
        bins = lr.cqt_frequencies(84, lr.note_to_hz('C1'))
        return lr.hz_to_midi(bins[np.argmax(profile)])


class EventExtractor:
    def extract(self, audio: Audio) -> list:
        onsets = lr.onset.onset_detect(audio.data, backtrack=True, units="samples")
        events = [Event(audio.data[0:onsets[0]])]
        for i in range(len(onsets) - 1):
            events.append(Event(audio.data[onsets[i]:onsets[i+1]]))
        events.append(Event(audio.data[onsets[-1]:-1]))
        for event in events: self.classify(event)
        return random.choices(events, k=5)

    def classify(self, event: Event):
        event.type = random.choice(["melodic", "textural", "percussive"])