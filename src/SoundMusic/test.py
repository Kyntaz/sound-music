import SoundMusic as sm
import time
import os
import pickle
import librosa as lr
import numpy as np

def do(file, out, svm=None):
    try:
        os.mkdir(f"../output/{out}")
    except FileExistsError:
        pass

    print("Opening sound.")
    source = sm.sound.load(f"../dataset/{file}")

    print("Extracting sounds.")
    lso = sm.extraction.get_sounds(source)

    print("Generating Synths.")
    if svm == None:
        synths, svm = sm.synth.evolve(sm.synth.SoundSynth, lso)
        with open(f"../output/{out}/svm.pickle", "wb") as f:
            pickle.dump(svm, f)
    else:
        with open(svm, "rb") as f:
            synths = sm.synth.fast_evolve(sm.synth.SoundSynth, lso, pickle.load(f))

    print("Making samplers.")
    samplers = sm.sample.make_samplers(sm.sample.Sampler3, synths, lso)

    print("Generating musical model.")
    model = sm.mustruct.build_model(5, source)

    print("Generating structures.")
    structs = sm.mustruct.make_structs(samplers, model)

    print("Generating song.")
    density = np.mean(lr.feature.spectral_flatness(source.samples)) * 0.2
    song = sm.mustruct.make_song(structs, density)
    fragments = song.get_sound()

    print("Generating drone.")
    drone1 = sm.drone.sevolve(source, fragments.duration + 10, 0.05)

    print("Writing audio.")
    fragments.write(f"../output/{out}/fragments.wav")
    drone1.write(f"../output/{out}/drone.wav")

    print("Writing midi.")
    song.save_midi(f"../output/{out}/fragments.mid")

    print("Modulating the drone.")
    points = song.get_instants()
    points = [[s, e, 0.1] for s,e in points]
    drone = sm.drone.side_chain(points, drone1)

    print("Generating final piece.")
    piece = sm.sound.join([drone, fragments])
    piece.write(f"../output/{out}/dry.wav")
    room = sm.effects.get_room(source, 1.0)
    verb = sm.effects.reverberate(room, piece)
    piece = sm.SoundObject(piece.samples + verb.get_normalize_to(0.5).samples)
    piece.write(f"../output/{out}/piece.wav")
    room.write(f"../output/{out}/room.wav")

    print("Generating stereo version")
    song1 = sm.mustruct.make_song(structs, density / 2)
    song2 = sm.mustruct.make_song(structs, density / 2)
    frags1 = song1.get_sound()
    frags2 = song2.get_sound()
    dur = max([frags1.duration, frags2.duration]) + 10.0
    drone1 = sm.drone.sevolve(source, dur, 0.01)
    drone2 = sm.drone.sevolve(source, dur, 0.05)

    points = song1.get_instants()
    points = [[s, e, 0.1] for s,e in points]
    drone1 = sm.drone.side_chain(points, drone1)

    points = song1.get_instants()
    points = [[s, e, 0.1] for s,e in points]
    drone2 = sm.drone.side_chain(points, drone2)

    piece_L = sm.sound.join([drone1, frags1])
    piece_R = sm.sound.join([drone2, frags2])
    verb_L = sm.effects.reverberate(room, piece_L)
    verb_R = sm.effects.reverberate(room, piece_R)
    piece_L = sm.SoundObject(piece_L.samples + verb_L.get_normalize_to(0.5).samples)
    piece_R = sm.SoundObject(piece_R.samples + verb_R.get_normalize_to(0.5).samples)
    sm.sound.write_stereo(piece_L, piece_R, 0.75, f"../output/{out}/stereo.wav")

    print("Done")

def do_drone(file, out):
    try:
        os.mkdir(f"../output/{out}")
    except FileExistsError:
        pass

    print("Opening sound.")
    source = sm.sound.load(f"../dataset/{file}")

    print("Evolving drone.")
    drone_wave = sm.drone.sevolve(source, 90, 1.0)

    print("Saving.")
    drone_wave.write(f"../output/{out}/drone.wav")