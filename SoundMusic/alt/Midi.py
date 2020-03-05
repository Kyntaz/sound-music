from SoundMusic.Audio import Audio
from SoundMusic.AudioSegmentation import AudioSegmenter
from SoundMusic.FeatureExtraction import FeatureExtractor
from SoundMusic.EventExtraction import EventExtractor
from SoundMusic.InstrumentGeneration import InstrumentGenerator
from SoundMusic.MotifComposition import MotifComposer
from SoundMusic.Arranging import Arranger
from SoundMusic.AudioRendering import AudioRenderer
from SoundMusic.GeneticAlgorithm import GeneticAlgorithm
from SoundMusic.utils.MidiConvert import read_midi
from SoundMusic.Architecture import System
import SoundMusic.utils.Ranges as ranges
import random, math, copy

class MidiSystem(System):
    def __init__(self):
        self.audio_segmenter = AudioSegmenter()
        self.feature_extractor = FeatureExtractor()
        self.event_extractor = EventExtractor()
        self.instrument_generator = InstrumentGenerator()
        self.motif_composer = MotifComposer()
        self.arranger = Arranger()
        self.audio_renderer = AudioRenderer()
        self.genetic_algorithm = GeneticAlgorithm()
    
    def process(self, audio: Audio, out: str, mid: str=""):
        print("Starting processing...")
        print(f"Reading midi file {mid}.")
        piece = read_midi(mid)
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
        instruments = self.instrument_generator.generate(events, len(events) // 10)
        print("Generated {} instruments.".format(len(instruments)))

        for line in piece.lines:
            b_instrument = None
            d = math.inf
            l_range = line.range()
            instruments_s = copy.copy(instruments)
            random.shuffle(instruments_s)
            for instrument in instruments_s:
                i_range = instrument.range()
                under = max(i_range[0] - l_range[0], 0)
                over = max(l_range[1] - i_range[1], 0)
                dd = under + over
                if dd < d:
                    d = dd
                    b_instrument = instrument
            line.instrument = b_instrument
        
        print("Rendering the audio.")
        output = self.audio_renderer.render(piece, audio.smpRt, out)
        print("Processing done!")
        debug = {
            "segments": segments,
            "features": features,
            "events": events,
            "instruments": instruments,
            "piece": piece
        }
        return (output, debug)
