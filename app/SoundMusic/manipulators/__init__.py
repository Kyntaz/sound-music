import SoundMusic.manipulators.compound
from SoundMusic.manipulators.Ghosts import Ghosts
from SoundMusic.manipulators.short import Identity, Flatten, RandomFilter, LengthFilter, BandPass, Reverse, PitchShift, PositionShift, Speed, Echo
from SoundMusic.manipulators.split import BeatSplit, OnsetSplit
from SoundMusic.manipulators.Complement import Complement
from SoundMusic.manipulators.granulate import GranularShuffle, GranularReverse, Granulate
from SoundMusic.manipulators.modulate import Modulate, WaveMod

as_list = [
    Ghosts,
    #Identity,
    Flatten,
    RandomFilter,
    LengthFilter,
    BandPass,
    Reverse,
    PitchShift,
    PositionShift,
    Speed,
    Echo,
    BeatSplit,
    OnsetSplit,
    Complement,
    GranularShuffle,
    GranularReverse,
    Granulate,
    Modulate,
    WaveMod
]