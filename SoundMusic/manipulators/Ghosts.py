import SoundMusic as sm
from SoundMusic.manipulators.base import ISimpleManipulator
import librosa as lr
import numpy as np
from pysndfx import AudioEffectsChain as Fx

class Ghosts(ISimpleManipulator):
    
    def __init__(self):
        self.amp = 0.5
        self.n_notes = 3
        self.dur = 1

    def do(self, sounds):
        sound = sm.render.render_audio(sounds)
        lso = []
        fft = lr.stft(sound.samples)
        fft_a = np.abs(fft)
        fft_a /= fft_a.max()
        fft_ph = np.angle(fft)
        fs = lr.fft_frequencies(sound.rate)
        onsets = lr.onset.onset_detect(
            sound.samples, sound.rate,
            units='frames'
        )
        for onset in onsets:
            time = lr.frames_to_time(onset, sound.rate)
            profile = fft_a[:,onset]
            phases = fft_ph[:,onset]
            n = self.n_notes
            sort = np.argsort(profile)[-n:]
            freqs = [fs[i] for i in sort]
            amps = [profile[i] for i in sort]
            phs = [phases[i] for i in sort]
            for f,a,ph in zip(freqs, amps, phs):
                wave = a * np.sin(np.linspace(
                    ph * f * 2 * np.pi,
                    (ph + self.dur) * f * 2 * np.pi,
                    self.dur * sound.rate))
                fade = sm.processing.fade(sound.rate * self.dur * 0.1, wave.size)
                so = sm.sound.SoundObject(wave*fade, sound.rate, time)
                lso.append(so)
        return lso