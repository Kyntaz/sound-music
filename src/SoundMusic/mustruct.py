import collections
import copy
import random
import librosa as lr
import numpy as np
import SoundMusic as sm
from SoundMusic import SoundObject
import mido

# Note comparison epsilons:
FREQ_EPS = 2
MAG_EPS = 0.1
DUR_EPS = 0.1

TIME_VAR = 1.0
MIN_STRUCT_SIZE = 5
MAX_STRUCT_SIZE = 20
SONG_LEN = 90

# Genetic algorithm params:
POPULATION = 10
GENERATIONS = 5
ELITISM = 0.5
MUTATION_PITCH = 10.0
MUTATION_MAG = 0.3
MUTATION_DUR = 1.0

Note = collections.namedtuple("Note", "pitch, mag, dur")

class NoteObject:
    def __init__(self, note, sampler, t):
        self.note = note
        self.sampler = sampler
        self.t = t
        self.sound = None

    def get_sound(self) -> SoundObject:
        if self.sound != None:
            return self.sound
        so = self.sampler.play(*self.note)
        so.t = self.t
        self.sound = so
        return so

    def get_sounds(self):
        return [self.get_sound()]

    def get_midi(self):
        if self.note.pitch <= 0:
            return []

        midi_pitch = int(round(lr.hz_to_midi(self.note.pitch)))
        midi_vel = min(int(round(self.note.mag * 127)), 127)
        midi_time = int(round(mido.second2tick(self.t, 480, 500000)))
        midi_dur = int(round(mido.second2tick(self.note.dur, 480, 500000)))

        if midi_pitch <= 0:
            return []

        return [([
            mido.Message(
                "note_on",
                note=midi_pitch,
                velocity=midi_vel,
                time=midi_time
            ),
            mido.Message(
                "note_off",
                note=midi_pitch,
                velocity=midi_vel,
                time=midi_time+midi_dur
            )
        ], self.sampler)]

class Structure:
    def __init__(self, sub_structs, t):
        self.sub_structs = sub_structs
        self.t = t

    def get_sounds(self):
        sounds = []
        for struct in self.sub_structs:
            abs_struct = copy.deepcopy(struct)
            abs_struct.t += self.t
            sounds += abs_struct.get_sounds()
        return sounds

    def get_sound(self):
        return sm.sound.join(self.get_sounds())

    def get_midi(self):
        track_messages = []
        samplers = []
        midi_time = int(round(mido.second2tick(self.t, 480, 500000)))

        for struct in self.sub_structs:
            tracks = struct.get_midi()
            for notes, sampler in tracks:
                if not sampler in samplers:
                    samplers.append(sampler)
                    track_messages.append([])
                idx = samplers.index(sampler)
                new_notes = []
                for note in notes:
                    new_notes.append(note.copy(time=int(note.time+midi_time)))
                track_messages[idx] += new_notes
        
        return list(zip(track_messages, samplers))

    def save_midi(self, filename):
        track_messages = self.get_midi()
        midifile = mido.MidiFile(type=1)
        midifile.ticks_per_beat = 480

        for messages, _ in track_messages:
            miditrack = mido.MidiTrack()
            ordered_messages = sorted(messages, key=lambda mnote: mnote.time)
            new_messages = [ordered_messages[0]]
            for msg1,msg2 in zip(ordered_messages, ordered_messages[1:]):
                new_msg = msg2.copy(time=msg2.time-msg1.time)
                new_messages.append(new_msg)
            miditrack.extend(new_messages)
            midifile.tracks.append(miditrack)

        midifile.save(filename)

    def get_instants(self):
        out = []
        for struct in self.sub_structs:
            start = struct.t
            end = struct.get_sound().end
            out.append([start, end])
        return out

def build_model(n, source: SoundObject):
    model = []
    history = []

    onsets = lr.onset.onset_detect(
        source.samples, sr=sm.sound.SAMPLE_RATE,
        backtrack=True, units="samples", wait=int(0.1 * sm.sound.SAMPLE_RATE / 512)
    )
    for o1,o2 in zip(onsets, onsets[1:]):
        if o2 - o1 < sm.sound.SAMPLE_RATE * 0.1:
            continue
        so = SoundObject(source.samples[o1:o2])
        ptrack, mtrack = so.track_pitch()
        
        pitch = max(np.mean(ptrack), 0)
        mag = max(np.mean(mtrack), 0)
        dur = max(so.duration, 0.15)

        note = Note(pitch, mag, dur)
        history.append(note)
        history = history[-n:]

        model.append(history)
    return model

def notes_close_enough(n1: Note, n2: Note):
    return (
        n1.pitch - n2.pitch < FREQ_EPS and
        n1.mag - n2.mag < MAG_EPS and
        n1.dur - n2.dur < DUR_EPS
    )

def generate_note(history, model):
    potential = []
    for entry in model:
        for n1,n2 in zip(reversed(history), reversed(entry[:-1])):
            if not notes_close_enough(n1, n2): break
        else:
            potential.append(entry[:len(history)+1][-1])
    if len(potential) == 0:
        max_len = max([len(en) for en in model])
        partial = history[-max_len:]
        return generate_note(partial[1:], model)
    else:
        return random.choice(potential)

def generate_struct(samplers, model, size, prev_notes=None):
    notes = prev_notes or []
    while len(notes) < size:
        note = generate_note(notes, model)
        notes.append(note)
    
    lno = []
    t_ptr = 0
    sampler = random.choice(samplers)
    for note in notes:
        t = max(random.normalvariate(t_ptr, TIME_VAR), 0)
        lno.append(NoteObject(note, sampler, t))
        t_ptr += note.dur

    return Structure(lno, 0)
    
def mutate_struct(struct: Structure, samplers, model):
    notes = [n.note for n in struct.sub_structs]
    notes = notes[:random.randint(0, len(notes))]
    new_notes = []
    for note in notes:
        new_note = Note(
            max(random.normalvariate(note.pitch, MUTATION_PITCH), 0.0),
            max(random.normalvariate(note.mag, MUTATION_MAG), 0.0),
            max(random.normalvariate(note.dur, MUTATION_DUR), 0.15)
        )
        new_notes.append(new_note)
    size = random.randint(MIN_STRUCT_SIZE, MAX_STRUCT_SIZE)
    return generate_struct(samplers, model, size, new_notes)

def fitness(struct: Structure):
    while True:
        try:
            so = struct.get_sound()
            so.play()
            score = float(input("score > "))
            sm.sound.stop()
            break
        except ValueError:
            sm.sound.stop()
            print("Invalid Score...")
    return score

def evolve_struct(samplers, model):
    population = []
    for _ in range(POPULATION):
        size = random.randint(MIN_STRUCT_SIZE, MAX_STRUCT_SIZE)
        struct = generate_struct(samplers, model, size)
        fit = fitness(struct)
        population.append([struct, fit])
    
    for _ in range(GENERATIONS):
        elite = int(POPULATION * ELITISM)
        new_population = sorted(population, key=lambda snf: snf[1])[-elite:]

        possible_parents = []
        while len(new_population) < POPULATION:
            if len(possible_parents) < 2:
                possible_parents = copy.copy(population)
            
            parent = random.choices(
                possible_parents,
                weights=[ss[1] for ss in possible_parents],
                k=1
            )[0]
            possible_parents.remove(parent)
            
            child = mutate_struct(parent[0], samplers, model)
            fit = fitness(child)
            new_population.append([child, fit])
        
        population = new_population
    
    return population

def make_structs(samplers, model):
    return [
        generate_struct(
            samplers, model,
            random.randint(MIN_STRUCT_SIZE, MAX_STRUCT_SIZE)
        )
        for _ in range(POPULATION)
    ]

def make_song(structs, density):
    density = max(density, 0.1)
    n_structs = int(round(density * SONG_LEN))

    out = []
    for _ in range(n_structs):
        struct = copy.copy(random.choice(structs))
        struct.t = random.uniform(0, SONG_LEN)
        out.append(struct)

    return Structure(out, 0)
