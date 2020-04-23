# Render SoundObjects into a single SoundObject.
from SoundMusic.sound import SoundObject
from typing import List
import numpy as np
import math
from pysndfx import AudioEffectsChain as Fx

def render_audio(sounds: List[SoundObject], rate: int=-1, fade: float=0, pretty: bool=False):
    if rate < 0: rate = sounds[0].rate
    duration = max([so.end() for so in sounds]) + fade
    canvas = np.zeros(math.ceil(duration * rate))
    for so in sounds:
        st = math.floor(so.t * rate)
        et = st + so.samples.size
        canvas[st:et] += so.samples
    if pretty:
        canvas /= np.max(canvas)
        canvas = (
            Fx()
            .normalize()
            .reverb()
        )(canvas)
    return SoundObject(canvas, rate)