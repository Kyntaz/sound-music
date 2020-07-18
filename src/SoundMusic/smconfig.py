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
    in_path, out_path, gens, elitism, flatness_weight, flatness_target,
    bandwidth_weight, bandwidth_target, target_weight, target_path,
    model_weight, model_path
):
    weights = [
        flatness_weight,
        bandwidth_weight,
        target_weight,
        model_weight
    ]
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    params = [
        flatness_target,
        bandwidth_target,
        sm.sound.load(target_path),
        model
    ]
    source = sm.sound.load(in_path)
    lso = sm.extraction.get_sounds(source)
    config = sm.gensound.evolve(lso, gens, elitism, weights, params)

    out = ""
    i = 0
    for so,pitch,vel in config:
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
        gens = int(sys.argv[4])
        elitism = float(sys.argv[5])
        flatness_weight = float(sys.argv[6])
        flatness_target = float(sys.argv[7])
        bandwidth_weight = float(sys.argv[8])
        bandwidth_target = float(sys.argv[9])
        target_weight = float(sys.argv[10])
        target_path = sys.argv[11]
        model_weight = float(sys.argv[12])
        model_path = sys.argv[13]
        print(f"Generating synth PCM samples for audio at '{in_path}', writing into '{out_path}'.")
        synth_config(
            in_path, out_path, gens, elitism, flatness_weight, flatness_target,
            bandwidth_weight, bandwidth_target, target_weight, target_path,
            model_weight, model_path
        )
    else:
        print(f"Configuration target '{sys.argv[1]}' not recognized.")

if __name__=="__main__":
    main()