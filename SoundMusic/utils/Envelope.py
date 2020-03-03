import numpy as np
from math import floor

def adsr(l, attack=(0.2, 1.0), decay=(0, 1.0), sustain=(0.6, 1.0), release=(0.2, 0.0)):
    attack_form = np.linspace(0, attack[1], floor(attack[0] * l))
    decay_form = np.linspace(attack[1], decay[1], floor(decay[0] * l))
    sustain_form = np.linspace(decay[1], sustain[1], floor(sustain[0] * l))
    release_form = np.linspace(sustain[1], release[1], floor(release[0] * l))
    return np.concatenate((attack_form, decay_form, sustain_form, release_form))

def apply(wave, envelope):
    return wave[:len(envelope)] * envelope