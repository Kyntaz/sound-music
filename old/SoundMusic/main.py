from SoundMusic.Audio import Audio
from SoundMusic.Architecture import System
import SoundMusic.utils.Exceptions as exceptions
import sys, os, traceback

def main():
    process_dataset(System(), sys.argv[0], sys.argv[1])

def process_dataset(system, s, l):
    outs = []
    debugs = []
    dataset = get_dataset()
    for i, f in enumerate(dataset[s:s+l]):
        try:
            print(f"Reading audio file {f}...")
            audio = Audio.from_path(f)
            print("Read successfuly.")
            out, debug = system.process(audio, f"output/{i}.wav")
            debug["filename"] = f
            outs.append(out)
            debugs.append(debug)
        except Exception as e: exceptions.save_exception(e)
    return (outs, debugs)

def get_dataset():
    return ['./dataset/{}'.format(f) for f in os.listdir('./dataset')]

if __name__ == "__main__": main()