from SoundMusic.Audio import Audio

class FeatureExtractor:
    def __init__(self, features: list=[]):
        self.features = features
    
    def add_feature(self, feature):
        self.features.append(feature)

    def extract(self, audio: Audio) -> dict:
        extracted = {}
        for feature in self.features:
            extracted[type(feature).__name__.lower()] = feature.get(audio)
        return extracted

    def is_feature(self, cl):
        self.add_feature(cl())
        return cl