import SoundMusic as sm
import librosa as lr
import numpy as np
import os
import pickle
import mido

VERB_LEN = 1.0

def mono(in_path, out_path, svm, midi=True, fg=True, bg=True, ssnds=True):
    out = out_path

    try:
        os.mkdir(out_path)
    except FileExistsError:
        pass

    print("Opening sound.")
    source = sm.sound.load(in_path)

    print("Extracting sounds.")
    lso = sm.extraction.get_sounds(source)

    print("Generating Synths.")
    if os.path.splitext(svm) == ".svm":
        with open(svm, "rb") as f:
            synths = sm.synth.fast_evolve(sm.synth.SoundSynth, lso, pickle.load(f))
    else:
        synths = []
        #sm.synth.GENERATIONS = 20
        for f in os.listdir(svm):
            print(f"Making a synth for {f}")
            path_to_f = os.path.join(svm, f)
            target = sm.sound.load(path_to_f)
            population = sm.synth.fast_evolve(sm.synth.SoundSynth, lso, target)
            synths.append(population[0])

    print("Making samplers.")
    samplers = sm.sample.make_samplers(sm.sample.Sampler3, synths, lso, False, out)

    print("Saving Samplers.")
    for i, sampler in enumerate(samplers):
        sampler.save(f"{out}/instrument{i}.synth")

    print("Generating musical model.")
    model = sm.mustruct.build_model(5, source)

    print("Writing musical model")
    model_txt = ""
    for entry in model:
        for note in entry:
            model_txt += f"{note[0]}, {note[1]}, {note[2]}; "
        model_txt += "\n"
    with open(f"{out}/model.seq", "w") as file:
        file.write(model_txt)

    print("Generating structures.")
    structs = sm.mustruct.make_structs(samplers, model)

    print("Saving structures.")
    for i,struct in enumerate(structs):
        struct.save_midi(f"{out}/motif{i}.mid")
        struct.get_sound().write(f"{out}/motif{i}.wav")

    print("Generating song.")
    song = sm.mustruct.evolve_song(structs)
    fragments = song.get_sound()

    print("Generating drone.")
    drone1 = sm.drone.sevolve(source, fragments.duration + 10, 0.05)

    print("Writing audio.")
    if fg: fragments.write(f"{out}/fragments.wav")
    if bg: drone1.write(f"{out}/drone.wav")

    print("Writing midi.")
    if midi: song.save_midi(f"{out}/fragments.mid")

    print("Modulating the drone.")
    points = song.get_instants()
    points = [[s, e, 0.1] for s,e in points]
    drone = sm.drone.side_chain(points, drone1)

    print("Generating final piece.")
    piece = sm.sound.join([drone, fragments])
    piece.write(f"{out}/dry.wav")
    room = sm.effects.get_room(source, VERB_LEN)
    if room != None:
        verb = sm.effects.reverberate(room, piece)
        piece = sm.SoundObject(piece.samples + verb.get_normalize_to(0.5).samples)
    piece.write(f"{out}/mono.wav")
    if room != None: room.write(f"{out}/room.wav")

def stereo(in_path, out_path, svm=None, midi=True, fg=True, bg=True, ssnds=True):
    svm = svm or "../svm.pickle"
    out = out_path
    file = in_path

    try:
        os.mkdir(out)
    except FileExistsError:
        pass

    print("Opening sound.")
    source = sm.sound.load(file)

    print("Extracting sounds.")
    lso = sm.extraction.get_sounds(source)

    print("Generating Synths.")
    if os.path.splitext(svm) == ".svm":
        with open(svm, "rb") as f:
            synths = sm.synth.fast_evolve(sm.synth.SoundSynth, lso, pickle.load(f))
    else:
        synths = []
        #sm.synth.GENERATIONS = 20
        for f in os.listdir(svm):
            print(f"Making a synth for {f}")
            path_to_f = os.path.join(svm, f)
            target = sm.sound.load(path_to_f)
            population = sm.synth.fast_evolve(sm.synth.SoundSynth, lso, target)
            synths.append(population[0])

    print("Making samplers.")
    samplers = sm.sample.make_samplers(sm.sample.Sampler3, synths, lso, False, out)

    print("Saving Samplers.")
    for i, sampler in enumerate(samplers):
        sampler.save(f"{out}/instrument{i}.synth")

    print("Generating musical model.")
    model = sm.mustruct.build_model(5, source)

    print("Writing musical model")
    model_txt = ""
    for entry in model:
        for note in entry:
            model_txt += f"{note[0]}, {note[1]}, {note[2]}; "
        model_txt += "\n"
    with open(f"{out}/model.seq", "w") as file:
        file.write(model_txt)

    print("Generating structures.")
    structs = sm.mustruct.make_structs(samplers, model)

    print("Saving structures.")
    for i,struct in enumerate(structs):
        struct.save_midi(f"{out}/motif{i}.mid")
        struct.get_sound().write(f"{out}/motif{i}.wav")

    print("Generating song.")
    song1 = sm.mustruct.evolve_song(structs)
    fragments1 = song1.get_sound()
    song2 = sm.mustruct.evolve_song(structs)
    fragments2 = song2.get_sound()

    print("Generating drone.")
    dur = max([fragments1.duration, fragments2.duration])
    drone1 = sm.drone.sevolve(source, dur + 10, 0.05)
    drone2 = sm.drone.sevolve(source, dur + 10, 0.05)

    print("Writing audio.")
    if fg:
        fragments1.write(f"{out}/fragmentsL.wav")
        fragments2.write(f"{out}/fragmentsR.wav")
    if bg:
        drone2.write(f"{out}/droneR.wav")
        drone1.write(f"{out}/droneL.wav")

    print("Writing midi.")
    if midi:
        song1.save_midi(f"{out}/fragmentsL.mid")
        song2.save_midi(f"{out}/fragmentsR.mid")

    print("Modulating the drone.")
    points = song1.get_instants()
    points = [[s, e, 0.1] for s,e in points]
    drone1 = sm.drone.side_chain(points, drone1)
    points = song2.get_instants()
    points = [[s, e, 0.1] for s,e in points]
    drone2 = sm.drone.side_chain(points, drone2)

    print("Generating final piece.")
    piece1 = sm.sound.join([drone1, fragments1])
    piece1.write(f"{out}/dryL.wav")
    piece2 = sm.sound.join([drone2, fragments2])
    piece2.write(f"{out}/dryR.wav")
    room = sm.effects.get_room(source, VERB_LEN)
    if room != None:
        verb1 = sm.effects.reverberate(room, piece1)
        verb2 = sm.effects.reverberate(room, piece2)
        piece1 = sm.SoundObject(piece1.samples + verb1.get_normalize_to(0.5).samples)
        piece2 = sm.SoundObject(piece2.samples + verb2.get_normalize_to(0.5).samples)
    piece1.write(f"{out}/monoL.wav")
    piece2.write(f"{out}/monoR.wav")
    if room != None: room.write(f"{out}/room.wav")
    sm.sound.write_stereo(piece1, piece2, 0.75, f"{out}/stereo.wav")

def render_midi_mono(in_path, out_path, midi_path, svm=None):
    svm = svm or "../svm.pickle"
    out = out_path
    file = in_path

    try:
        os.mkdir(f"{out}")
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
    samplers = sm.sample.make_samplers(sm.sample.Sampler3, synths, lso, n_samplers=n_samplers)

    print("Generate song.")
    song = sm.mustruct.read_midi(midi_path, samplers)
    fragments = song.get_sound()

    print("Generating drone.")
    drone1 = sm.drone.sevolve(source, fragments.duration, 0.05)

    print("Writing audio.")
    fragments.write(f"{out}/fragments.wav")
    drone1.write(f"{out}/drone.wav")

    print("Modulating the drone.")
    drone = sm.drone.side_chain([], drone1)

    print("Generating final piece.")
    piece = sm.sound.join([drone, fragments])
    piece.write(f"{out}/dry.wav")
    room = sm.effects.get_room(source, VERB_LEN)
    verb = sm.effects.reverberate(room, piece)
    piece = sm.SoundObject(piece.samples + verb.get_normalize_to(0.5).samples)
    piece.write(f"{out}/mono.wav")
    room.write(f"{out}/room.wav")

def test(in_path, out_path, svm=None, midi=True, fg=True, bg=True, ssnds=True):
    svm = svm or "../svm.pickle"
    out = out_path

    try:
        os.mkdir(out_path)
    except FileExistsError:
        pass

    print("Opening sound.")
    source = sm.sound.load(in_path)

    print("Extracting sounds.")
    lso = sm.extraction.get_sounds(source)

    print("Generating Synths.")
    with open(svm, "rb") as f:
        synths = sm.topsynth.evolve(lso, pickle.load(f))

    print("Making samplers.")
    samplers = sm.sample.make_samplers(sm.sample.Sampler3, synths, lso, ssnds, out)

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
    if fg: fragments.write(f"{out}/fragments.wav")
    if bg: drone1.write(f"{out}/drone.wav")

    print("Writing midi.")
    if midi: song.save_midi(f"{out}/fragments.mid")

    print("Modulating the drone.")
    points = song.get_instants()
    points = [[s, e, 0.1] for s,e in points]
    drone = sm.drone.side_chain(points, drone1)

    print("Generating final piece.")
    piece = sm.sound.join([drone, fragments])
    piece.write(f"{out}/dry.wav")
    room = sm.effects.get_room(source, VERB_LEN)
    verb = sm.effects.reverberate(room, piece)
    piece = sm.SoundObject(piece.samples + verb.get_normalize_to(0.5).samples)
    piece.write(f"{out}/mono.wav")
    room.write(f"{out}/room.wav")