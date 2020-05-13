import SoundMusic as sm
from SoundMusic.sound import SoundObject
from SoundMusic.manipulators.base import ISimpleManipulator
import librosa as lr
import numpy as np

class OnsetSplit(ISimpleManipulator):

    def do(self, sounds):
        sound = sm.render.render_audio(sounds)
        onsets = lr.onset.onset_detect(sound.samples, sound.rate,
            units='samples', backtrack=True)
        lso = []
        for o1, o2 in zip(onsets, onsets[1:]):
            samples = sound.samples[o1:o2]
            t = lr.samples_to_time(o1, sound.rate)
            so = SoundObject(samples, sound.rate, t + sound.t)
            lso.append(so)
        return lso

class BeatSplit(ISimpleManipulator):

    def do(self, sounds):
        sound = sm.render.render_audio(sounds)
        _, beats = lr.beat.beat_track(sound.samples, sound.rate,
            units='samples', start_bpm=60.0)
        lso = []
        for b1, b2 in zip(beats, beats[1:]):
            samples = sound.samples[b1:b2]
            t = lr.samples_to_time(b1, sound.rate)
            so = SoundObject(samples, sound.rate, t + sound.t)
            lso.append(so)
        return lso