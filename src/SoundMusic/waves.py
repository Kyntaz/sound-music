import numpy as np
import SoundMusic as sm


def sin(t, fr, am, ph):
    return np.sin(t * 2 * np.pi * fr + ph) * am

def square(t, fr, am, ph):
    return np.sign(sin(t, fr, 1.0, ph)) * am

def saw(t, fr, am, ph):
    return (((t * fr + ph) % 1.0) - 0.5) * am * 2.0

def triangle(t, fr, am, ph):
    return (np.abs(saw(t, fr, 1.0, ph)) * 2.0 - 1.0) * am

def bump(t, s, p, w):
    return np.nan_to_num(
        np.logical_and(((t - p) / w) <= 1, ((t - p) / w) >= -1) *
        np.exp(- 1.0 / (1 - ((t - p) / w)**2))
    ) * s * 2.5

def tspan(dur):
    return np.linspace(0, dur, int(np.round(dur * sm.sound.SAMPLE_RATE)))
