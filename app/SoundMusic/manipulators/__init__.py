import SoundMusic.manipulators.compound
from SoundMusic.manipulators.Ghosts import Ghosts, SquareGhosts
from SoundMusic.manipulators.short import Identity, Flatten, RandomFilter, LengthFilter, BandPass, Reverse, PitchShift, PositionShift, Speed, Echo, TimeMagnet
from SoundMusic.manipulators.split import BeatSplit, OnsetSplit
from SoundMusic.manipulators.Complement import Complement
from SoundMusic.manipulators.granulate import GranularShuffle, GranularReverse, ScatterGrains
from SoundMusic.manipulators.modulate import Modulate, WaveMod

as_list = [
    #Identity,
    Ghosts,
    SquareGhosts,
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
    ScatterGrains,
    Modulate,
    WaveMod,
    TimeMagnet
]