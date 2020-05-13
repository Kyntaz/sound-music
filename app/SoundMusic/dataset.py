# Automatically probe the dataset folder:
import os
from SoundMusic.sound import SoundObject

_dataset = {}

def init_dataset():
    global _dataset
    dataset_path = "dataset/"
    for file in os.listdir(dataset_path):
        name = os.path.splitext(file)[0]
        _dataset[name] = dataset_path + file

def read(name):
    global _dataset
    return SoundObject.load(_dataset[name])

def get():
    global _dataset
    return list(_dataset.keys())

#init_dataset()