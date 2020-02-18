import librosa as lr

class Audio:
    def __init__(self, path):
        self.data, self.smpRt = lr.load(path)
        self.annotations = {} # for caching

    def annotate(self, key: str, note):
        self.annotations[key] = note

def read_dataset(index: int) -> Audio:
    return Audio("./dataset/{}.wav".format(index))