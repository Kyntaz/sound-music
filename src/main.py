from Architecture import SYSTEM
from Audio import read_dataset
import Features
import Instruments
import sys

def process_dataset(s, l):
    for i in range(s, l):
        print("Reading audio file {}...".format(i))
        audio = read_dataset(i)
        print("Read successfuly.")
        SYSTEM.process(audio)

def main():
    process_dataset(sys.argv[0], sys.argv[1])

#if __name__ == "__main__":
#    main()