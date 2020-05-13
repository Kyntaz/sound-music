# Objects to manipulate sounds.
import librosa as lr
import soundfile as sf
import numpy as np

class SoundObject:

    def __init__(self, samples, rate, t=0):
        if samples is None:
            print("Warning: Creating an empty sound object.")
        self.samples = samples
        self.rate = rate
        self.t = t

    @staticmethod
    def load(path):
        samples, rate = lr.load(path)
        return SoundObject(samples, rate)

    def write(self, path):
        sf.write(path, self.samples, self.rate)

    def duration(self):
        return lr.samples_to_time(self.samples.size, self.rate)

    def end(self):
        return self.t + self.duration()