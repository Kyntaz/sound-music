import librosa

class Audio:
    def __init__(self, path):
        self.data, self.smpRt = librosa.load(path)
        self.annotations = {}

    def annotate(self, key: str, note):
        self.annotations[key] = note

def read_dataset(index: int) -> Audio:
    return Audio("./dataset/{}.wav".format(index))