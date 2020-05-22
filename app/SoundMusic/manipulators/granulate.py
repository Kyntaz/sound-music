import SoundMusic as sm
import numpy as np
from SoundMusic.manipulators.base import ISimpleManipulator, tweak_function
from SoundMusic.sound import SoundObject
import copy
import random
import time

class GranularShuffle(ISimpleManipulator):

    def __init__(self):
        self.density = 100
        self.seed = 202016041830

    def tweak(self, power):
        self.density += np.clip(random.uniform(-1,1) * 950 * power, 50, 1000)
        self.seed = time.time()

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        random.seed(self.seed)
        lso = []
        for so in sounds:
            n_grans = np.round(self.density * so.duration())
            splits = np.linspace(0, so.samples.size, int(n_grans))
            splits = np.floor(splits)
            grans = []
            for s1, s2 in zip(splits, splits[1:]):
                gran = so.samples[int(s1):int(s2)]
                fade = sm.processing.fade(0.1 * gran.size, gran.size)
                grans.append(gran*fade)
            random.shuffle(grans)
            if len(grans) <= 0:
                lso.append(so)
                continue
            samples = np.concatenate(grans)
            nso = SoundObject(samples, so.rate, so.t)
            lso.append(nso)
        return lso

class GranularReverse(ISimpleManipulator):

    def __init__(self):
        self.density = 100

    def tweak(self, power):
        self.density += np.clip(random.uniform(-1,1) * 950 * power, 50, 1000)

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        lso = []
        for so in sounds:
            n_grans = np.round(self.density * so.duration())
            splits = np.linspace(0, so.samples.size, int(n_grans))
            splits = np.floor(splits)
            grans = []
            for s1, s2 in zip(splits, splits[1:]):
                gran = so.samples[int(s1):int(s2)]
                fade = sm.processing.fade(0.1 * gran.size, gran.size)
                grans.append(gran*fade)
            grans.reverse()
            if len(grans) <= 0:
                lso.append(so)
                continue
            samples = np.concatenate(grans)
            nso = SoundObject(samples, so.rate, so.t)
            lso.append(nso)
        return lso

class ScatterGrains(ISimpleManipulator):

    def __init__(self):
        self.seed = 187
        self.density = 10
        self.scatter = 1


    def tweak(self, power):
        self.density += np.clip(random.uniform(-1,1) * 150 * power, 50, 200)
        self.scatter += tweak_function(0.01, 10.0, power)
        self.seed = time.time()

    def do(self, sounds):
        random.seed(self.seed)
        sounds = copy.deepcopy(sounds)
        lso = []
        shift = 0
        for so in sounds:
            n_grans = np.round(self.density * so.duration())
            if n_grans < 1:
                lso.append(so)
                continue
            grans = []
            splits = np.linspace(0, so.samples.size, int(n_grans))
            splits = np.floor(splits)
            for s1, s2 in zip(splits, splits[1:]):
                gran = so.samples[int(s1):int(s2)]
                fade = sm.processing.fade(0.1 * gran.size, gran.size)
                gran *= fade
                t = shift + random.uniform(-self.scatter, self.scatter)
                t = max(t, 0.0)
                nso = SoundObject(gran, so.rate, t)
                grans.append(nso)
                shift += nso.duration()
            nso = sm.render.render_audio(grans)
            nso.t = so.t
            lso.append(nso)
        return lso