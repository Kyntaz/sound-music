# This file contains definitions of commands to be run in the REPL.
import context
import audio
import system
import sounddevice as sd
import notes
import generators
import soundfile as sf
import ffmpeg
import winsound
import preprocessors

class CommandNotFoundError(Exception): pass

def do(action, args):
    global _all_commands
    if not action in _all_commands: raise CommandNotFoundError()
    f = _all_commands[action]
    f(*args)

# Commands:

def print_command(*args):
    print(" ".join(args))

def def_command(name, val):
    context.define(name, val)

def reset_command():
    context.clear()
    system.reset()

def list_dataset():
    dataset = audio.get_dataset()
    print(", ".join(dataset.keys()))

def hear_command(id):
    audio.read_dataset(id).play()

def stop_command():
    sd.stop()

def load_audio(id):
    s = system.get_system()
    s.set_audio(audio.read_dataset(id))

def play_audio():
    s = system.get_system()
    s.audio_source.play()

def list_midis():
    midis = notes.get_midis()
    print(", ".join(midis.keys()))

def load_midi(id):
    s = system.get_system()
    midi = notes.read_midi(id)
    print(", ".join([l.name for l in midi]))
    s.set_midi(midi)

def list_generators():
    gens = generators.get_generators()
    print(", ".join(gens.keys()))

def add_generator(id, name):
    s = system.get_system()
    gen_class = generators.get_generator(id)
    gen = gen_class()
    params = gen.get_parameters()
    if params != None:
        user_params = {}
        print(f"{id} generator setup:")
        for param in params:
            user_in = input(f"{param} ({params[param]}) $ ")
            if len(user_in) == 0:
                user_params[param] = params[param]
            elif isinstance(params[param], str):
                user_params[param] = user_in
            else:
                user_val = eval(user_in)
                user_params[param] = user_val
        gen.set_parameters(user_params)
    s.add_generator(name, gen)
    print(f"Created gen {name}!")

def command_pure():
    s = system.get_system()
    s.generate_pure()
    winsound.Beep(440, 500); winsound.Beep(880, 500)

def play_output():
    s = system.get_system()
    sd.play(s.output.samples, s.output.rate)

def save(name):
    s = system.get_system()
    sf.write(f"output/{name}.wav", s.output.samples, s.output.rate)
    (
        ffmpeg
        .input(f"output/{name}.wav")
        .output(f"output/{name}.mp3")
        .run(quiet=True)
    )

def save_system(name):
    system.save(name)
    print("Success!")

def load_system(name):
    system.load(name)
    print("Success!")

def add_preprocessor(id, name):
    s = system.get_system()
    preprocessor_class = preprocessors.get_preprocessor(id)
    preprocessor = preprocessor_class()
    params = preprocessor.get_parameters()
    if params != None:
        user_params = {}
        print(f"{id} preprocessor setup:")
        for param in params:
            user_in = input(f"{param} ({params[param]}) $ ")
            if len(user_in) == 0:
                user_params[param] = params[param]
            elif isinstance(params[param], str):
                user_params[param] = user_in
            else:
                user_val = eval(user_in)
                user_params[param] = user_val
        preprocessor.set_parameters(user_params)
    s.add_preprocessor(name, preprocessor)
    print(f"Created preprocessor {name}!")

def test_preprocess():
    s = system.get_system()
    s.preprocess()

def list_preprocessors():
    pres = preprocessors.get_preprocessors()
    print(", ".join(pres.keys()))

def process_all(name):
    data = audio.get_dataset()
    for key in data.keys():
        print(f"Processing {key}")
        try:
            load_audio(key)
            command_pure()
            save(f"{name}_{key}")
            print("Success!")
        except:
            print("Failed...")

# =====

# Mapping all commands to their name:
_all_commands = {
    "print": print_command,
    "def": def_command,
    "reset": reset_command,
    "dset": list_dataset,
    "hear": hear_command,
    "stop": stop_command,
    "laudio": load_audio,
    "paudio": play_audio,
    "midis": list_midis,
    "lmidi": load_midi,
    "lgens": list_generators,
    "gen": add_generator,
    "pure": command_pure,
    "pout": play_output,
    "sout": save,
    "s": save_system,
    "l": load_system,
    "pre": add_preprocessor,
    "tpre": test_preprocess,
    "lpre": list_preprocessors,
    "pureall": process_all,
}