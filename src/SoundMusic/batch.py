import os.path
from glob import glob
import random
import SoundMusic as sm
import traceback as tb

def get_name(file):
    return os.path.basename(os.path.splitext(file)[0])

def do(n):
    files = glob("../dataset/*")
    for _ in range(n):
        try:
            file = random.choice(files)
            files.remove(file)
            name = get_name(file)
            sm.test.do(file, f"batch-{name}", "../svm.pickle")
        except KeyboardInterrupt:
            return
        except:
            continue

def stereo(n, inp, out, svm):
    files = glob(f"{inp}/*")
    for _ in range(n):
        try:
            fileN = random.choice(files)
            file = os.path.join(inp, fileN)
            print(f"Inspiration from {fileN}")
            files.remove(fileN)
            name = get_name(file)
            sm.generation.stereo(file, f"{out}/batch-{name}", svm)
        except KeyboardInterrupt:
            return
        except:
            tb.print_exc()
            continue