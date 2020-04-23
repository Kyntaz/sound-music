import SoundMusic as sm
from SoundMusic.sound import SoundObject
from SoundMusic.manipulators.base import ISimpleManipulator
import copy
import random
from pysndfx import AudioEffectsChain as Fx
import numpy as np

class Identity(ISimpleManipulator):

    def do(self, sounds):
        return copy.deepcopy(sounds)

class Flatten(ISimpleManipulator):

    def do(self, sounds):
        return [sm.render.render_audio(sounds)]

class LengthFilter(ISimpleManipulator):

    def __init__(self):
        self.limit = 0.2

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        return list(filter(lambda so: so.duration() > self.limit, sounds))

class RandomFilter(ISimpleManipulator):

    def __init__(self):
        self.limit = 0.5
        self.seed = 202004161456

    def do(self, sounds):
        random.seed(self.seed)
        sounds = copy.deepcopy(sounds)
        return list(filter(lambda so: random.random() < self.limit, sounds))

class BandPass(ISimpleManipulator):

    def __init__(self):
        self.low = 100
        self.high = 2000

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        for so in sounds:
            so.samples = (
                Fx()
                .lowpass(self.low)
                .highpass(self.high)
            )(so.samples)
        return sounds

class Reverse(ISimpleManipulator):

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        for so in sounds:
            so.samples = np.flip(so.samples)
        return sounds

class PitchShift(ISimpleManipulator):

    def __init__(self):
        self.bias = 0
        self.var = 12
        self.seed = 202016041830

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        random.seed(self.seed)
        for so in sounds:
            so.samples = (
                Fx()
                .pitch(random.normalvariate(self.bias, self.var))
            )(so.samples)
        return sounds

class Speed(ISimpleManipulator):
     
    def __init__(self):
        self.bias = 1
        self.var = 1
        self.seed = 202016041830

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        random.seed(self.seed)
        for so in sounds:
            ratio = np.clip(random.normalvariate(self.bias, self.var), 0.1, 100)
            so.samples = (
                Fx()
                .tempo(ratio)
            )(so.samples)
        return sounds

class PositionShift(ISimpleManipulator):

    def __init__(self):
        self.bias = 0
        self.var = 10
        self.seed = 202016041830

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        random.seed(self.seed)
        for so in sounds:
            so.t += random.normalvariate(self.bias, self.var)
            so.t = max(so.t, 0)
        return sounds

class Echo(ISimpleManipulator):
    
    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        for so in sounds:
            so.samples = (
                Fx()
                .delay()
            )(so.samples)
        return sounds
    
class Amplify(ISimpleManipulator):

    def __init__(self):
        self.amp = 1.1

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        for so in sounds:
            so.samples *= self.amp
        return sounds