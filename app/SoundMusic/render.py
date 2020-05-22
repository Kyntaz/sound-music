# Render SoundObjects into a single SoundObject.
from SoundMusic.sound import SoundObject
from typing import List
import numpy as np
import math
from pysndfx import AudioEffectsChain as Fx
import librosa as lr

def render_audio(sounds: List[SoundObject], rate: int=-1, fade: float=0, pretty: bool=False, trim: bool=True):
    sounds = list(filter(lambda so: isinstance(so.samples, np.ndarray) \
        and so.samples.size > 0, sounds))
    if len(sounds) <= 0:
        print("Warning: Rendering 0 sounds.")
        return SoundObject(np.array([]), 22050)
    if rate < 0: rate = sounds[0].rate
    duration = max([so.end() for so in sounds]) + fade
    canvas = np.zeros(math.ceil(duration * rate))
    for so in sounds:
        st = math.floor(so.t * rate)
        et = st + so.samples.size
        canvas[st:et] += so.samples
    if trim:
        canvas, _ = lr.effects.trim(canvas)
    if pretty:
        canvas /= np.max(canvas)
        canvas = (
            Fx()
            .normalize()
            .reverb()
        )(canvas)
    return SoundObject(canvas, rate)