import SoundMusic as sm
import librosa as lr
import numpy as np
import sys
import pickle
import os.path

def sequencer_config(in_path, out_path, n):
    source = sm.sound.load(in_path)
    model = sm.mustruct.build_model(n, source)
    model = [[(
        int(lr.hz_to_midi(note.pitch)) if note.pitch > 0.0 else 0,
        int(np.clip(note.mag, 0, 1) * 127),
        round(note.dur, 3)
    ) for note in entry] for entry in model]
    out = ""
    for entry in model:
        for note in entry:
            out += f"{note[0]}, {note[1]}, {note[2]}; "
        out += "\n"
    with open(out_path, "w") as file:
        file.write(out)

def synth_config(
    in_path, out_path, model_path,
    gens, mutation, elitism, var_mut
):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    source = sm.sound.load(in_path)
    lso = sm.extraction.get_sounds(source)

    sm.synth.POPULATION = len(lso)
    sm.synth.GENERATIONS = gens
    sm.synth.AVG_MUTATIONS = mutation
    sm.synth.ELITISM = elitism
    sm.synth.VAR_MUTATIONS = var_mut

    synths = sm.synth.fast_evolve(sm.synth.SoundSynth, lso, model)
    config = [synth.gen(so) for synth,so in zip(synths, lso)]

    out = ""
    i = 0
    for so in config:
        ptrack, vtrack = so.track_pitch()
        pitch = lr.hz_to_midi(np.mean(ptrack))
        vel = np.clip(np.mean(vtrack) * 127, 0, 127)
        path = os.path.dirname(out_path)
        fname = os.path.splitext(os.path.basename(out_path))[0] + f"_s{i}.wav"
        so.write(os.path.join(path, fname))
        out += f"{fname}, {pitch}, {vel}\n"
        i += 1

    with open(out_path, "w") as file:
        file.write(out)

def main():
    if (sys.argv[1] == "sequencer"):
        in_path = sys.argv[2]
        out_path = sys.argv[3]
        n = int(sys.argv[4])
        print(f"Generating sequencer configuration from audio at '{in_path}', considering {n}-grams, and writing into '{out_path}'.")
        sequencer_config(in_path, out_path, n)
    if (sys.argv[1] == "synth"):
        in_path = sys.argv[2]
        out_path = sys.argv[3]
        model_path = sys.argv[4]
        gens = int(sys.argv[5])
        mutation = float(sys.argv[6])
        elitism = float(sys.argv[7])
        var_mut = float(sys.argv[7])
        print(f"Generating synth PCM samples for audio at '{in_path}', writing into '{out_path}'.")
        synth_config(
            in_path, out_path, model_path,
            gens, mutation, elitism, var_mut
        )
    else:
        print(f"Configuration target '{sys.argv[1]}' not recognized.")

if __name__=="__main__":
    main()