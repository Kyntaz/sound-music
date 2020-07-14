import SoundMusic as sm
import librosa as lr
import numpy as np
import sys

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

def main():
    if (sys.argv[1] == "sequencer"):
        in_path = sys.argv[2]
        out_path = sys.argv[3]
        n = int(sys.argv[4])
        print(f"Generating sequencer configuration from audio at '{in_path}', considering {n}-grams, and writing into '{out_path}'.")
        sequencer_config(in_path, out_path, n)
    else:
        print(f"Configuration target '{sys.argv[1]}' not recognized.")

if __name__=="__main__":
    main()