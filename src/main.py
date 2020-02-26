from Architecture import SYSTEM
from Audio import Audio
import Features
import Instruments
import sys, os, traceback

def process_dataset(s, l):
    outs = []
    dataset = get_dataset()
    for i, f in enumerate(dataset[s:s+l]):
        try:
            print(f"Reading audio file {f}...")
            audio = Audio.from_path(f)
            print("Read successfuly.")
            out = SYSTEM.process(audio, f"output/{i}.wav")
            outs.append(out)
        except Exception:
            traceback.print_exc()
            pass
    return outs

def get_dataset():
    return ['./dataset/{}'.format(f) for f in os.listdir('./dataset')]

def main():
    process_dataset(sys.argv[0], sys.argv[1])

#if __name__ == "__main__":
#    main()