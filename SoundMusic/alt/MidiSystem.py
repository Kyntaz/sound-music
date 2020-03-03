from SoundMusic import SYSTEM
from SoundMusic.Audio import Audio
from SoundMusic.Architecture import System
from SoundMusic.utils.MidiConvert import read_midi
import random

class MidiSystem(System):
    def __init__(self):
        self.audio_segmenter = SYSTEM.audio_segmenter
        self.feature_extractor = SYSTEM.feature_extractor
        self.event_extractor = SYSTEM.event_extractor
        self.instrument_generator = SYSTEM.instrument_generator
        self.motif_composer = SYSTEM.motif_composer
        self.arranger = SYSTEM.arranger
        self.audio_renderer = SYSTEM.audio_renderer
        self.genetic_algorithm = SYSTEM.genetic_algorithm
    
    def process(self, audio: Audio, out: str, mid: str=""):
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
        instruments = self.instrument_generator.generate(events)
        print("Generated {} instruments.".format(len(instruments)))
        print(f"Reading midi file {mid}.")
        piece = read_midi(mid)
        for line in piece.lines:
            line.instrument = random.choice(instruments)
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

MIDI_SYSTEM = MidiSystem()