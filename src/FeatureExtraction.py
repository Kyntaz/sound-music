from Audio import Audio

class FeatureExtractor:
    def __init__(self, features: list=[]):
        self.features = features
    
    def add_feature(self, feature):
        self.features.append(feature)

    def extract(self, audio: Audio) -> list:
        return [feature(audio) for feature in self.features]

    def segments_extract(self, segments) -> list:
        return [self.extract(audio) for audio in segments]

def is_feature(extractor: FeatureExtractor):
    def add_to_extractor(func):
        extractor.add_feature(func)
        return func
    return add_to_extractor