import SoundMusic as sm
from SoundMusic.manipulators.base import IManipulator
import random

class ChainManipulator(IManipulator):

    def __init__(self, manipulators):
        self.manipulators = manipulators

    def do(self, sounds):
        for manip in self.manipulators:
            sounds = manip.do(sounds)
        return sounds

    def get_random(self):
        return random.choice(self.manipulators).get_random()

class StackManipulator(IManipulator):

    def __init__(self, manipulators):
        self.manipulators = manipulators

    def do(self, sounds):
        out = []
        for manip in self.manipulators:
            out += manip.do(sounds)
        return out

    def get_random(self):
        return random.choice(self.manipulators).get_random()

as_list = [
    ChainManipulator,
    StackManipulator
]