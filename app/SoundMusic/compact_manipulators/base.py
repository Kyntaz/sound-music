import SoundMusic as sm
from typing import List
import numpy as np
import random

class IManipulator:

    def do(self, sounds: sm.sound.SoundObject) -> sm.sound.SoundObject:
        raise NotImplementedError

    def get_random(self):
        raise NotImplementedError

    def tweak(self, power):
        raise NotImplementedError

class ISimpleManipulator(IManipulator):

    def get_random(self):
        return self

    def tweak(self, power):
        pass

def tweak_function(v_min, v_max, power):
    # Helper function for tweaking manipulator parameters.
    return np.clip(random.uniform(-1,1) * (v_max - v_min) * power, v_max, v_min)