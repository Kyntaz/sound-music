# Reading and handling audio files.
import librosa as lr
import os
import sounddevice as sd

class Audio:
    def __init__(self, samples, rate):
        self.samples = samples
        self.rate = rate
    
    @staticmethod
    def read(filepath):
        samples, rate = lr.load(filepath)
        return Audio(samples, rate)

    def play(self):
        sd.play(self.samples, self.rate)

# Automatically probe the dataset folder:
_dataset = {}

def init_dataset():
    global _dataset
    dataset_path = "dataset/"
    for file in os.listdir(dataset_path):
        name = os.path.splitext(file)[0]
        _dataset[name] = dataset_path + file

def read_dataset(name):
    global _dataset
    return Audio.read(_dataset[name])

def get_dataset():
    global _dataset
    return _dataset
