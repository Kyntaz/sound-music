from Architecture import SYSTEM
from Audio import Audio
import numpy as np
import librosa
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
            tempo, beats = librosa.beat.beat_track(audio.data)
            audio.annotate("tempo", tempo)
            audio.annotate("beats", beats)
        else:
            tempo = audio.annotations["tempo"]
        return tempo

@SYSTEM.is_feature
class TimeSignature:
    def get(self, audio: Audio):
        if not "beats" in audio.annotations:
            tempo, beats = librosa.beat.beat_track(audio.data)
            audio.annotate("tempo", tempo)
            audio.annotate("beats", beats)
        else:
            beats = audio.annotations["beats"]
        if not "chroma" in audio.annotations:
            chroma = librosa.feature.chroma_cqt(audio.data)
            chroma = librosa.util.sync(chroma, beats)
            audio.annotate("chroma", chroma)
        recurrence = librosa.segment.recurrence_matrix(chroma, sym=True, mode="distance")
        candidates = list(range(3, 13))
        time_signatures = get_time_signature(recurrence, candidates)
        return candidates[np.argmax(time_signatures)]

