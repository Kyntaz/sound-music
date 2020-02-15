from Audio import Audio
from AudioSegmentation import AudioSegmenter
from FeatureExtraction import FeatureExtractor
from EventExtraction import EventExtractor
from InstrumentGeneration import InstrumentGenerator
from MotifComposition import MotifComposer
from Arranging import Arranger
from AudioRendering import AudioRenderer
from GeneticAlgorithm import GeneticAlgorithm

class System:
    def __init__(self):
        self.audio_segmenter = AudioSegmenter()
        self.feature_extractor = FeatureExtractor()
        self.event_extractor = EventExtractor()
        self.instrument_generator = InstrumentGenerator()
        self.motif_composer = MotifComposer()
        self.arranger = Arranger()
        self.audio_renderer = AudioRenderer()
        self.genetic_algorithm = GeneticAlgorithm()
    
    def is_feature(self, func):
        return self.feature_extractor.is_feature(func)

    def is_instrument(self, cl):
        return self.instrument_generator.is_instrument(cl)

    def process(self, audio: Audio):
        print("Starting processing...")
        print("Segmenting audio...")
        segments = self.audio_segmenter.segment(audio)
        print("Segmentation done. Audio split into {} segments".format(len(segments)))
        print("Extracting features...")
        features = [self.feature_extractor.extract(segment) for segment in segments]
        print("Features extracted!")
        print("Extracting events...")
        events = sum([self.event_extractor.extract(audio) for segment in segments], [])
        print("Extracted {} events.".format(len(events)))
        print("Generating instruments...")
        instruments = [self.instrument_generator.generate(event) for event in events]
        print("Generated {} instruments.".format(len(instruments)))
        print("Generating motifs...")
        motifs = sum([self.motif_composer.compose(feature, instruments) for feature in features], [])
        print("Generated {} motifs.".format(len(motifs)))
        print("Arranging pieces...")
        pieces = self.arranger.arrange(instruments, features, motifs)
        print("Prepared {} pieces.".format(len(pieces)))
        print("Running the genetig algorithm...")
        piece, score = self.genetic_algorithm.ga(pieces)
        print("Genetic algorithm completed with score {}.".format(score))
        print("Rendering audio...")
        self.audio_renderer.render(piece)
        print("Processing done!")

SYSTEM = System()