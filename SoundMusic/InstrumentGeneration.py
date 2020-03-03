from SoundMusic.EventExtraction import Event
import random
import numpy as np
import sklearn as skl
import librosa as lr
import traceback


class InstrumentGenerator:
    def __init__(self, instrument_classes: list=[]):
        self.instrument_classes = instrument_classes
        self.instruments = []

    def add_instrument_class(self, instrument):
        self.instrument_classes.append(instrument)

    def generate(self, events: list):
        clusters = skl.cluster.AgglomerativeClustering(n_clusters=5)
        feats = []
        r_events = []
        for event in events:
            try:
                feat = np.mean(lr.amplitude_to_db(np.abs(lr.stft(event.data))), axis=1)
                feats.append(feat)
                r_events.append(event)
            except: traceback.print_exc()
        clusters.fit(feats)
        instruments = [random.choice(self.instrument_classes)() for _ in range(clusters.n_clusters_)]
        for i,c in enumerate(clusters.labels_):
            instruments[c].add_event(r_events[i])
        instruments = list(filter(lambda inst: self.validate_instrument(inst), instruments))
        assert len(instruments) > 0
        return instruments

    def validate_instrument(self, instrument):
        return True

    def is_instrument(self, cl):
        self.add_instrument_class(cl)
        return cl