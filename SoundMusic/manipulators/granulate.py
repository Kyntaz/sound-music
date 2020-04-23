import SoundMusic as sm
import numpy as np
from SoundMusic.manipulators.base import ISimpleManipulator
from SoundMusic.sound import SoundObject
import copy
import random

class GranularShuffle(ISimpleManipulator):

    def __init__(self):
        self.density = 100
        self.seed = 202016041830

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
            if len(grans) <= 0: continue
            samples = np.concatenate(grans)
            nso = SoundObject(samples, so.rate, so.t)
            lso.append(nso)
        return lso

class GranularReverse(ISimpleManipulator):

    def __init__(self):
        self.density = 100

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
            if len(grans) <= 0: continue
            samples = np.concatenate(grans)
            nso = SoundObject(samples, so.rate, so.t)
            lso.append(nso)
        return lso

class Granulate(ISimpleManipulator):

    def __init__(self):
        self.density = 10

    def do(self, sounds):
        sounds = copy.deepcopy(sounds)
        lso = []
        shift = 0
        for so in sounds:
            n_grans = np.round(self.density * so.duration())
            splits = np.linspace(0, so.samples.size, int(n_grans))
            splits = np.floor(splits)
            for s1, s2 in zip(splits, splits[1:]):
                gran = so.samples[int(s1):int(s2)]
                fade = sm.processing.fade(0.1 * gran.size, gran.size)
                gran *= fade
                nso = SoundObject(gran, so.rate, so.t + shift)
                lso.append(nso)
                shift += nso.duration()
        return lso