import SoundMusic.compact_manipulators.compound
from SoundMusic.compact_manipulators.Ghosts import Ghosts, SquareGhosts
from SoundMusic.compact_manipulators.short import RandomFilter, LengthFilter, BandPass, Reverse, PitchShift, PositionShift, Speed, Echo, TimeMagnet
from SoundMusic.compact_manipulators.Complement import Complement
from SoundMusic.compact_manipulators.granulate import GranularShuffle, GranularReverse, ScatterGrains
from SoundMusic.compact_manipulators.modulate import Modulate, WaveMod

as_list = [
    Ghosts,
    SquareGhosts,
    RandomFilter,
    LengthFilter,
    BandPass,
    Reverse,
    PitchShift,
    PositionShift,
    Speed,
    Echo,
    Complement,
    GranularShuffle,
    GranularReverse,
    ScatterGrains,
    Modulate,
    WaveMod,
    TimeMagnet
]