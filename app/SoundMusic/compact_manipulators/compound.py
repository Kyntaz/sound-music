import SoundMusic as sm
from SoundMusic.compact_manipulators.base import IManipulator
import random
import numpy as np

class Chain(IManipulator):

    def __init__(self, manipulators):
        self.manipulators = manipulators

    def do(self, sound):
        for manip in self.manipulators:
            print(f"Doing {type(manip).__name__}")
            sound = manip.do(sound)
        return sound

    def get_random(self):
        return random.choice(self.manipulators).get_random()

    def tweak(self, power):
        for m in self.manipulators: m.tweak(power)

class Stack(IManipulator):

    def __init__(self, manipulators):
        self.manipulators = manipulators

    def do(self, sound):
        out = []
        for manip in self.manipulators:
            print(f"Doing {type(manip).__name__}")
            out += [manip.do(sound)]
        return sm.render.render_audio(out)

    def get_random(self):
        return random.choice(self.manipulators).get_random()

    def tweak(self, power):
        for m in self.manipulators: m.tweak(power)

as_list = [
    Chain,
    Stack
]