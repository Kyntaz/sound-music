import librosa as lr

class Audio:
    def __init__(self, data, smpRt):
        self.data = data
        self.smpRt = smpRt
        self.annotations = {}        

    @staticmethod
    def from_path(path):
        data, smpRt = lr.load(path)
        return Audio(data, smpRt)

    def cache(self, key, func):
        if not key in self.annotations:
            self.annotations[key] = func()
        return self.annotations[key]

def read_dataset(index: int) -> Audio:
    return Audio.from_path("./dataset/{}.wav".format(index))