from Architecture import SYSTEM
from Audio import Audio
import numpy as np
import librosa as lr
from utils.TimeSignature import get_time_signature

@SYSTEM.is_feature
class Classification:
    def get(self, audio: Audio):
        try: audio.annotations["class"]
        except: return ""

@SYSTEM.is_feature
class Tempo:
    def get(self, audio: Audio):
        if not "tempo" in audio.annotations:
            tempo, beats = lr.beat.beat_track(audio.data)
            audio.annotate("tempo", tempo)
            audio.annotate("beats", beats)
        else:
            tempo = audio.annotations["tempo"]
        return tempo

@SYSTEM.is_feature
class TimeSignature:
    def get(self, audio: Audio):
        if not "beats" in audio.annotations:
            tempo, beats = lr.beat.beat_track(audio.data)
            audio.annotate("tempo", tempo)
            audio.annotate("beats", beats)
        else:
            tempo = audio.annotations["tempo"]
            beats = audio.annotations["beats"]
        if not "chroma" in audio.annotations:
            chroma = lr.feature.chroma_cqt(audio.data)
            chroma = lr.util.sync(chroma, beats)
            audio.annotate("chroma", chroma)
        recurrence = lr.segment.recurrence_matrix(chroma, sym=True, mode="distance")
        beat_dur = 60 / tempo
        candidates = list(filter(lambda x: x * beat_dur < 3.5, range(3,13)))
        time_signatures = get_time_signature(recurrence, candidates)
        return candidates[np.argmax(time_signatures)]

@SYSTEM.is_feature
class Scale:
    def get(self, audio: Audio):
        if not "chroma" in audio.annotations:
            chroma = lr.feature.chroma_cqt(audio.data)
            audio.annotate("chroma", chroma)
        else:
            chroma = audio.annotations["chroma"]
        chroma_profile = np.amax(chroma, axis=1)
        avg = (chroma_profile.max() + chroma_profile.min()) / 2
        scale = [i for i in range(len(chroma_profile)) if chroma_profile[i] > avg]
        return scale

