from SoundMusic.Audio import Audio
import numpy as np
import librosa as lr
from SoundMusic.utils.TimeSignature import get_time_signature

class Classification:
    def get(self, audio: Audio):
        try: return audio.annotations["class"]
        except: return ""

class Tempo:
    def get(self, audio: Audio):
        tempo, _ = audio.cache("beat_track", \
            lambda: lr.beat.beat_track(audio.data))
        return tempo

class TimeSignature:
    def get(self, audio: Audio):
        tempo, beats = audio.cache("beat_track", \
            lambda: lr.beat.beat_track(audio.data))
        chroma = audio.cache("chroma", \
            lambda: lr.util.sync(lr.feature.chroma_cqt(audio.data), beats))
        recurrence = lr.segment.recurrence_matrix(chroma, sym=True, mode="distance")
        beat_dur = 60 / tempo
        candidates = list(filter(lambda x: x * beat_dur < 3.5, range(3,13)))
        time_signatures = get_time_signature(recurrence, candidates)
        return candidates[np.argmax(time_signatures)]

class Scale:
    def get(self, audio: Audio):
        _, beats = audio.cache("beat_track", \
            lambda: lr.beat.beat_track(audio.data))
        chroma = audio.cache("chroma", \
            lambda: lr.util.sync(lr.feature.chroma_cqt(audio.data), beats))
        chroma_profile = np.amax(chroma, axis=1)
        avg = np.mean(chroma_profile)
        pot_scale = [i for i in range(len(chroma_profile)) if chroma_profile[i] > avg]
        scale = [pot_scale[0]]
        for i in range(1, len(pot_scale) - 1):
            if not (pot_scale[i-1] + 1 == pot_scale[i] and \
                pot_scale[i+1] - 1 == pot_scale[i] and pot_scale[i-1] in scale):
                scale.append(pot_scale[i])
        scale.append(pot_scale[-1])
        return scale

all_features = [
    Classification,
    Tempo,
    TimeSignature,
    Scale,
]