import SoundMusic as sm
from SoundMusic.sound import SoundObject
from SoundMusic.manipulators.base import ISimpleManipulator, tweak_function
import copy
import random
from pysndfx import AudioEffectsChain as Fx
import numpy as np
import time
import librosa as lr

class Identity(ISimpleManipulator):

    def do(self, sounds):
        return copy.deepcopy(sounds)

class Flatten(ISimpleManipulator):

    def do(self, sounds):
        return [sm.render.render_audio(sounds)]

class LengthFilter(ISimpleManipulator):

    def __init__(self):
        self.limit = 0.2

    def tweak(self, power):
        self.limit += np.clip(random.uniform(-1,1) * power, 0.1, 1.0)

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        return list(filter(lambda so: so.duration() > self.limit, sounds))

class RandomFilter(ISimpleManipulator):

    def __init__(self):
        self.limit = 0.5
        self.seed = 202004161456

    def tweak(self, power):
        self.limit += np.clip(random.uniform(-1,1) * power, 0.01, 0.99)
        self.seed = time.time()

    def do(self, sounds):
        random.seed(self.seed)
        sounds = copy.deepcopy(sounds)
        return list(filter(lambda so: random.random() < self.limit, sounds))

class BandPass(ISimpleManipulator):

    def __init__(self):
        self.low = 100
        self.high = 2000

    def tweak(self, power):
        self.low += np.clip(random.uniform(-1,1) * 2000 * power, 20, 2000)
        self.high += np.clip(random.uniform(-1,1) * 2000 * power, self.low, 20000)

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

    def tweak(self, power):
        self.bias += np.clip(random.uniform(-1,1) * 12 * power, -6, 6)
        self.var += np.clip(random.uniform(-1,1) * 12 * power, 0, 12)
        self.seed = time.time()

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        random.seed(self.seed)
        for so in sounds:
            try:
                so.samples = lr.effects.pitch_shift(
                    so.samples, so.rate,
                    random.normalvariate(self.bias, self.var)
                )
            except:
                print("Warning: Pitch shift failed.")
        return sounds

class Speed(ISimpleManipulator):
     
    def __init__(self):
        self.bias = 1
        self.var = 1
        self.seed = 202016041830

    def tweak(self, power):
        self.bias += np.clip(random.uniform(-1,1) * 8 * power, -4, 4)
        self.var += np.clip(random.uniform(-1,1) * 4 * power, 0, 4)
        self.seed = time.time()

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        random.seed(self.seed)
        for so in sounds:
            ratio = np.clip(random.normalvariate(self.bias, self.var), 0.1, 100)
            so.samples = lr.effects.time_stretch(so.samples, ratio)
        return sounds

class PositionShift(ISimpleManipulator):

    def __init__(self):
        self.bias = 0
        self.var = 10
        self.seed = 202016041830

    def tweak(self, power):
        self.bias += np.clip(random.uniform(-1,1) * 20 * power, -20, 20)
        self.var += np.clip(random.uniform(-1,1) * 60 * power, 0, 60)
        self.seed = time.time()

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        random.seed(self.seed)
        for so in sounds:
            so.t += random.normalvariate(self.bias, self.var)
            so.t = max(so.t, 0)
        return sounds

class Echo(ISimpleManipulator):

    def __init__(self):
        self.n = 3
        self.delay = 1.0
        self.decay = 0.5

    def tweak(self, power):
        self.n += int(np.clip(random.uniform(-1,1) * 10 * power, 1, 10))
        self.delay += np.clip(random.uniform(-1,1) * 10 * power, 0.01, 10)
        self.decay += np.clip(random.uniform(-1,1) * 0.9 * power, 0.01, 0.9)
    
    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        lso = []
        for so in sounds:
            lso.append(so)
            nso = so
            for _ in range(self.n):
                nso = SoundObject(nso.samples * self.decay, nso.rate, nso.t + self.delay)
                lso.append(nso)
        return lso
    
class Amplify(ISimpleManipulator):

    def __init__(self):
        self.amp = 1.1

    def tweak(self, power):
        self.amp += np.clip(random.uniform(-1,1) * 5 * power, 0.1, 5.0)

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        for so in sounds:
            so.samples *= self.amp
        return sounds

class TimeMagnet(ISimpleManipulator):

    def __init__(self):
        self.time = 2.0 / 3.0
        self.strength = 1.0
        self.radius = 10.0

    def tweak(self, power):
        self.time += tweak_function(0.0, 1.0, power)
        self.strength += tweak_function(-1.0, 1.0, power)
        self.radius += tweak_function(1.0, 120.0, power)

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        real_time = max([s.end() for s in sounds]) * self.time
        for sound in sounds:
            if abs(sound.t - real_time) < self.radius:
                sound.t += (real_time - sound.t) * self.strength
        return sounds