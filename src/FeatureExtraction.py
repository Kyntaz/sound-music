from Audio import Audio

class FeatureExtractor:
    def __init__(self, features: list=[]):
        self.features = features
    
    def add_feature(self, feature):
        self.features.append(feature)

    def extract(self, audio: Audio) -> list:
        return [feature(audio) for feature in self.features]

    def is_feature(self, func):
        self.add_feature(func)
        return func