import os.path
from glob import glob
import random
import SoundMusic as sm

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