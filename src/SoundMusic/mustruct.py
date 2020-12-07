import collections
import copy
import random
import librosa as lr
import numpy as np
import scipy as sp
import SoundMusic as sm
from SoundMusic import SoundObject
import mido
import matplotlib.pyplot as plt

# Note comparison epsilons:
FREQ_EPS = 2
MAG_EPS = 0.1
DUR_EPS = 0.1

TIME_VAR = 1.0
MIN_STRUCT_SIZE = 5
MAX_STRUCT_SIZE = 20
SONG_LEN = 90

# Genetic algorithm params:
POPULATION = 3
GENERATIONS = 3
ELITISM = 0.5
MUTATION_PITCH = 10.0
MUTATION_MAG = 0.3
MUTATION_DUR = 1.0

# Song Grammars
EMBRYO = [0, 1, 0]
COMPLEXITY = 3
GPASSES = 5
RULE_STEP = 3

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
        _, mtrack = so.track_pitch()
        
        pitch = max(so.get_f0(), 0)
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

def read_midi(path, samplers, polyphonic = False):
    mid = mido.MidiFile(path)
    out = []
    for i, track in enumerate(mid.tracks):
        sampler = samplers[i]
        notes = {}
        last_note = (None, 0, 0)
        t_ptr = 0

        for msg in track:
            t_ptr += msg.time
            tempo = 500000
            if msg.type == "note_on":
                notes[msg.note] = (t_ptr, msg.velocity / 255)
                if last_note[0] != None and not polyphonic:
                    note, start, vel = last_note
                    dur = t_ptr - start
                    dur = mido.tick2second(dur, mid.ticks_per_beat, tempo)
                    start = mido.tick2second(start, mid.ticks_per_beat, tempo)
                    if dur > 0.1:
                        note = NoteObject(Note(lr.midi_to_hz(msg.note), vel, dur), sampler, start)
                        out.append(note)
                last_note = (msg.note, t_ptr, msg.velocity / 255)
            if msg.type == "note_off":
                try:
                    start, vel = notes[msg.note]
                    dur = t_ptr - start
                    dur = mido.tick2second(dur, mid.ticks_per_beat, tempo)
                    start = mido.tick2second(start, mid.ticks_per_beat, tempo)
                    note = NoteObject(Note(lr.midi_to_hz(msg.note), vel, dur), sampler, start)
                    out.append(note)
                except:
                    print("Warning: Problems reading MIDI.")
            if msg.type == "set_tempo":
                tempo = msg.tempo
                print(f"Read MIDI tempo: {tempo}")

    return Structure(out, 0)

def make_rule(nstructs):
    return [
        random.randint(0, nstructs),
        [random.randint(0, nstructs) for _ in range(random.randint(1, COMPLEXITY))]
    ]

def make_sequence(grammar):
    seq = copy.copy(EMBRYO)
    for _ in range(GPASSES):
        nseq = []
        for sym in seq:
            for rule in grammar:
                head, body = copy.deepcopy(rule)
                if head == sym:
                    nseq += body
                    break
            else:
                nseq += [sym]
        seq = nseq
    return seq

def seq2song(seq, structs):
    out = []
    t = 10
    for sym in seq:
        struct = copy.deepcopy(structs[sym])
        dur = max(so.end for so in struct.get_sounds())
        struct.t = max(random.normalvariate(t, dur), 0)
        out.append(struct)
        t += dur
    return Structure(out, 0)

def song_fit(struct):
    so = struct.get_sound()
    fft = lr.stft(so.samples)
    tension = np.log(np.transpose(np.abs(fft)) @ lr.fft_frequencies(sm.sound.SAMPLE_RATE))
    tension = np.maximum(tension, 0)
    tension = sp.signal.resample(tension, int(so.duration))
    peak = np.argmax(tension)
    hi = np.max(tension)
    low = np.min(tension)
    gold_peak = so.duration / sp.constants.golden

    return abs(low - hi) - abs(so.duration - 60) / 10 - abs(peak - gold_peak)

def evolve_song(structs):
    nstructs = len(structs) - 1
    pop = [[make_rule(nstructs) for _ in range(RULE_STEP)] for _ in range(POPULATION)]
    last_gram = None
    last_score = - np.inf
    for _ in range(GENERATIONS):
        best_gram = pop[0]
        best_score = - np.inf
        for gram in pop:
            seq = make_sequence(gram)
            song = seq2song(seq, structs)
            score = song_fit(song)
            if score > best_score:
                best_gram = gram
                best_score = score
        if best_score < last_score:
            best_gram = last_gram
            best_score = last_score
        print(best_score)
        pop = [[make_rule(nstructs) for _ in range(RULE_STEP)] + best_gram for _ in range(POPULATION)]
        last_gram = best_gram
        last_score = best_score

    seq = make_sequence(best_gram)
    return seq2song(seq, structs)
