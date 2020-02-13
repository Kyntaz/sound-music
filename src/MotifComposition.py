from Music import Line

class MotifComposer:
    def compose(self, features: list, instruments: list) -> list:
        return []

    def segments_compose(self, feature_struct: list, instruments) -> list:
        return [self.compose(features, instruments) for features in feature_struct]