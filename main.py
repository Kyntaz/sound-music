# For testing only, right now...
import SoundMusic as sm

#sm.makerand.batch_experiment(10, 5, 10, sm.manipulators.as_list, sm.manipulators.compound.as_list, "randomT")

sm.makerand.batch_experiment(20, 1, 0, [sm.manipulators.WaveMod], sm.manipulators.compound.as_list, "modulateTest2")