import librosa

class Audio:
    def __init__(self, path):
        self.data = librosa.load(path)
        self.annotation = ""

    def annotate(self, note: str):
        self.annotation = note

def read_dataset(index: int) -> Audio:
    return Audio("./dataset/{}.wav".format(index))