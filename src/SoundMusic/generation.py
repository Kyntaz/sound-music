import SoundMusic as sm
import librosa as lr
import numpy as np
import os
import pickle
import mido


def mono(in_path, out_path, svm=None):
    svm = svm or "../svm.pickle"
    out = out_path
    file = in_path

    try:
        os.mkdir(f"../output/{out}")
    except FileExistsError:
        pass

    print("Opening sound.")
    source = sm.sound.load(f"../dataset/{file}")

    print("Extracting sounds.")
    lso = sm.extraction.get_sounds(source)

    print("Generating Synths.")
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
    piece.write(f"../output/{out}/mono.wav")
    room.write(f"../output/{out}/room.wav")

def stereo(in_path, out_path, svm=None):
    svm = svm or "../svm.pickle"
    out = out_path
    file = in_path

    try:
        os.mkdir(f"../output/{out}")
    except FileExistsError:
        pass

    print("Opening sound.")
    source = sm.sound.load(f"../dataset/{file}")

    print("Extracting sounds.")
    lso = sm.extraction.get_sounds(source)

    print("Generating Synths.")
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
    density /= 2.0
    song1 = sm.mustruct.make_song(structs, density)
    fragments1 = song1.get_sound()
    song2 = sm.mustruct.make_song(structs, density)
    fragments2 = song2.get_sound()

    print("Generating drone.")
    dur = max([fragments1.duration, fragments2.duration])
    drone1 = sm.drone.sevolve(source, dur + 10, 0.05)
    drone2 = sm.drone.sevolve(source, dur + 10, 0.05)

    print("Writing audio.")
    fragments1.write(f"../output/{out}/fragmentsL.wav")
    drone1.write(f"../output/{out}/droneL.wav")
    fragments2.write(f"../output/{out}/fragmentsR.wav")
    drone2.write(f"../output/{out}/droneR.wav")

    print("Writing midi.")
    song1.save_midi(f"../output/{out}/fragmentsL.mid")
    song2.save_midi(f"../output/{out}/fragmentsR.mid")

    print("Modulating the drone.")
    points = song1.get_instants()
    points = [[s, e, 0.1] for s,e in points]
    drone1 = sm.drone.side_chain(points, drone1)
    points = song2.get_instants()
    points = [[s, e, 0.1] for s,e in points]
    drone2 = sm.drone.side_chain(points, drone2)

    print("Generating final piece.")
    piece1 = sm.sound.join([drone1, fragments1])
    piece1.write(f"../output/{out}/dryL.wav")
    piece2 = sm.sound.join([drone2, fragments2])
    piece2.write(f"../output/{out}/dryR.wav")
    room = sm.effects.get_room(source, 1.0)
    verb1 = sm.effects.reverberate(room, piece1)
    verb2 = sm.effects.reverberate(room, piece2)
    piece1 = sm.SoundObject(piece1.samples + verb1.get_normalize_to(0.5).samples)
    piece2 = sm.SoundObject(piece2.samples + verb2.get_normalize_to(0.5).samples)
    piece1.write(f"../output/{out}/monoL.wav")
    piece2.write(f"../output/{out}/monoR.wav")
    room.write(f"../output/{out}/room.wav")
    sm.sound.write_stereo(piece1, piece2, 0.75, f"../output/{out}/stereo.wav")

def render_midi_mono(in_path, out_path, midi_path, svm=None):
    svm = svm or "../svm.pickle"
    out = out_path
    file = in_path

    try:
        os.mkdir(f"../output/{out}")
    except FileExistsError:
        pass

    print("Opening sound.")
    source = sm.sound.load(f"../dataset/{file}")

    print("Extracting sounds.")
    lso = sm.extraction.get_sounds(source)

    print("Generating Synths.")
    with open(svm, "rb") as f:
        synths = sm.synth.fast_evolve(sm.synth.SoundSynth, lso, pickle.load(f))

    print("Making samplers.")
    n_samplers = len(mido.MidiFile(midi_path).tracks)
    samplers = sm.sample.make_samplers(sm.sample.Sampler3, synths, lso, n_samplers)

    print("Generate song.")
    song = sm.mustruct.read_midi(midi_path, samplers)
    fragments = song.get_sound()

    print("Generating drone.")
    drone1 = sm.drone.sevolve(source, fragments.duration, 0.05)

    print("Writing audio.")
    fragments.write(f"../output/{out}/fragments.wav")
    drone1.write(f"../output/{out}/drone.wav")

    print("Modulating the drone.")
    drone = sm.drone.side_chain([], drone1)

    print("Generating final piece.")
    piece = sm.sound.join([drone, fragments])
    piece.write(f"../output/{out}/dry.wav")
    room = sm.effects.get_room(source, 1.0)
    verb = sm.effects.reverberate(room, piece)
    piece = sm.SoundObject(piece.samples + verb.get_normalize_to(0.5).samples)
    piece.write(f"../output/{out}/mono.wav")
    room.write(f"../output/{out}/room.wav")