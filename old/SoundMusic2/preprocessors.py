# Audio preprocessing to be applied before the composition process.
import librosa as lr
import numpy as np
import audio as audmod
import copy

class IPreprocessor:
    def get_parameters(self): return None
    def set_parameters(self, params): pass
    def preprocess(self, audio): raise NotImplementedError

class Complement(IPreprocessor):
    def preprocess(self, audio):
        audio = copy.deepcopy(audio)
        fft = lr.stft(audio.samples)
        fft_a = np.abs(fft)
        mask = fft_a > (fft_a.mean() * 10)
        fft_ph = np.angle(fft)
        fft_comp_ph = - fft_ph
        fft_comp_a = - fft_a + fft_a.max()
        fft_comp = fft_comp_a * (np.cos(fft_comp_ph) + 1j * np.sin(fft_comp_ph))
        fft_comp *= mask
        wave = lr.istft(fft_comp)
        return audmod.Audio(wave, audio.rate)

# Mapping from preprocessor classes to their name in the repl:
_preprocessors = {
    "complement": Complement,
}

def get_preprocessor(id):
    global _preprocessors
    return _preprocessors[id]

def get_preprocessors():
    global _preprocessors
    return _preprocessors