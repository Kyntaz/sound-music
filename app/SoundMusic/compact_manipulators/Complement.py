import librosa as lr
import SoundMusic as sm
from SoundMusic.compact_manipulators.base import ISimpleManipulator
from SoundMusic.sound import SoundObject
import copy
import numpy as np

class Complement(ISimpleManipulator):

    def do(self, sound):
        sound = copy.deepcopy(sound)
        lso = []
        try:
            fft = lr.stft(sound.samples)
            fft_a = np.abs(fft)
            mask = fft_a > (fft_a.mean() * 10)
            fft_ph = np.angle(fft)
            fft_comp_ph = - fft_ph
            fft_comp_a = - fft_a + fft_a.max()
            fft_comp = fft_comp_a * (np.cos(fft_comp_ph) + 1j * np.sin(fft_comp_ph))
            fft_comp *= mask
            wave = lr.istft(fft_comp)
            so = SoundObject(wave, sound.rate, sound.t)
            lso.append(so)
        except:
            print("Warning: Complement failed, adding original sound.")
            lso.append(sound)
        return sm.render.render_audio(lso)