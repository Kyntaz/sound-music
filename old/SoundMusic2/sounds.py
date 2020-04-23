# Structures to represent and render the final result.
import numpy as np
import audio
import math as mt
import time

class SoundObject:
    def __init__(self, samples, rate, t):
        self.samples = samples
        self.rate = rate
        self.t = t

    def get_dur(self):
        return self.samples.size / self.rate

    def get_end(self):
        return self.t + self.get_dur()

def last_sound_moment(sound_objects):
    ends = [s.get_end() for s in sound_objects]
    return max(ends)

def render(sound_objects, rate):
    e = last_sound_moment(sound_objects) + 5
    canvas = np.zeros(mt.ceil(e * rate))

    for sound in sound_objects:
        s = mt.floor(sound.t * rate)
        e = s + sound.samples.size
        canvas[s:e] += sound.samples
        
    return audio.Audio(canvas, rate)
    