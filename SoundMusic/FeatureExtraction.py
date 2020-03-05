from SoundMusic.Audio import Audio
from SoundMusic.Features import all_features

class FeatureExtractor:
    def __init__(self, features: list=None):
        if features == None:
            self.features = all_features
        else:
            self.features = features
    
    def add_feature(self, feature):
        self.features.append(feature)

    def extract(self, audio: Audio) -> dict:
        extracted = {}
        for feature in self.features:
            extractor = feature()
            extracted[type(feature).__name__.lower()] = extractor.get(audio)
        return extracted

    def is_feature(self, cl):
        self.add_feature(cl)
        return cl