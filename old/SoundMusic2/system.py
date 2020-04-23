import audio
import sounds
from pysndfx import AudioEffectsChain as Fx
import pickle

class SoundMusicSystem:
    def __init__(self):
        self.generators = {}
        self.midi_generators = {}
        self.preprocessors = {}
        self.sound_objects = []
        self.audio_source = None
        self.midi_source = []
        self.output = None

    def add_generator(self, name, generator):
        self.generators[name] = generator

    def add_midi_generator(self, name, generator):
        self.midi_generators[name] = generator

    def add_preprocessor(self, name, preprocessor):
        self.preprocessors[name] = preprocessor

    def init_generators(self):
        for generator in self.generators:
            generator.read_audio(self.audio_source)

    def preprocess(self):
        a = self.audio_source
        for preprocessor in self.preprocessors.values():
            a = preprocessor.preprocess(a)
        self.output = a
        return a

    def set_audio(self, audio):
        self.audio_source = audio

    def set_midi(self, lines):
        self.lines = lines

    def generate_pure(self):
        a = self.preprocess()
        self.sound_objects = []
        for generator in self.generators.values():
            lso = generator.generate(a)
            self.sound_objects += lso
        self.output = sounds.render(self.sound_objects, a.rate)
        self.output.samples = (
            Fx()
            .normalize()
            .reverb()
        )(self.output.samples)

_system = SoundMusicSystem()

def get_system():
    global _system
    return _system

def reset():
    global _system
    _system = SoundMusicSystem()

def save(name):
    global _system
    with open(f"systems/{name}.sm", "wb") as file:
        pickle.dump(_system, file)

def load(name):
    global _system
    with open(f"systems/{name}.sm", "rb") as file:
        _system = pickle.load(file)