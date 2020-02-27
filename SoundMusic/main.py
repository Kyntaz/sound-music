from SoundMusic.Architecture import SYSTEM
from SoundMusic.Audio import Audio
from SoundMusic import Features, Instruments
import sys, os, traceback

def process_dataset(s, l):
    outs = []
    debugs = []
    dataset = get_dataset()
    for i, f in enumerate(dataset[s:s+l]):
        try:
            print(f"Reading audio file {f}...")
            audio = Audio.from_path(f)
            print("Read successfuly.")
            out, debug = SYSTEM.process(audio, f"output/{i}.wav")
            debug["filename"] = f
            outs.append(out)
            debugs.append(debug)
        except: traceback.print_exc()
    return (outs, debugs)

def get_dataset():
    return ['./dataset/{}'.format(f) for f in os.listdir('./dataset')]

def main():
    process_dataset(sys.argv[0], sys.argv[1])

if __name__ == "__main__": main()