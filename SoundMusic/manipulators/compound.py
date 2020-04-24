import SoundMusic as sm
from SoundMusic.manipulators.base import IManipulator
import random
import numpy as np

class Chain(IManipulator):

    def __init__(self, manipulators):
        self.manipulators = manipulators

    def do(self, sounds):
        for manip in self.manipulators:
            sounds = manip.do(sounds)
        return sounds

    def get_random(self):
        return random.choice(self.manipulators).get_random()

    def tweak(self, power):
        for m in self.manipulators: m.tweak(power)

class Stack(IManipulator):

    def __init__(self, manipulators):
        self.manipulators = manipulators

    def do(self, sounds):
        out = []
        for manip in self.manipulators:
            out += manip.do(sounds)
        return out

    def get_random(self):
        return random.choice(self.manipulators).get_random()

    def tweak(self, power):
        for m in self.manipulators: m.tweak(power)

class Progression(IManipulator):

    def __init__(self, manipulators):
        self.manipulators = manipulators

    def do(self, sounds):
        if len(sounds) < len(self.manipulators):
            out = []
            for manip in self.manipulators:
                out += manip.do(sounds)
            return out
        sounds = sorted(sounds, key=lambda so: so.t)
        parts = np.array_split(sounds, len(self.manipulators))
        out = []
        for part, manip in zip(parts, self.manipulators):
            if part.size == 0:
                print("Warning: Progression fail.")
                continue
            out += manip.do(part.tolist())
        return out

    def get_random(self):
        return random.choice(self.manipulators).get_random()

    def tweak(self, power):
        for m in self.manipulators: m.tweak(power)

as_list = [
    Chain,
    Stack,
    Progression
]