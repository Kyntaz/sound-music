import SoundMusic as sm
import librosa as lr
import numpy as np
from SoundMusic import SoundObject
import random
from pysndfx import AudioEffectsChain as Fx
import copy

def crossover(so1: SoundObject, so2: SoundObject) -> SoundObject:
    so1 = copy.deepcopy(so1)
    so2 = copy.deepcopy(so2)
    env1 = sm.waves.sin(
        sm.waves.tspan(so1.duration),
        random.uniform(0.1, 4),
        1.0,
        random.uniform(0, 2*np.pi)
    )

    env2 = sm.waves.sin(
        sm.waves.tspan(so2.duration),
        random.uniform(0.1, 4),
        1.0,
        random.uniform(0, 2*np.pi)
    )

    so1.samples *= env1
    so2.samples *= env2
    so1.t = 0
    so2.t = random.uniform(0, so1.duration)

    return sm.sound.join([so1.get_normalize_to(0.5), so2.get_normalize_to(0.5)])

# Mutations:

def mutate_bandpass(so: SoundObject):
    lo = random.uniform(20, 20e3)
    hi = random.uniform(lo, 20e3)
    out = sm.effects.band_pass(so, lo, hi)
    return out

def mutate_reverse(so: SoundObject):
    samps = np.flip(so.samples)
    return SoundObject(samps)

def mutate_pitch(so: SoundObject):
    samps = lr.effects.pitch_shift(so.samples, sm.sound.SAMPLE_RATE, random.uniform(-12.0, 12.0))
    return SoundObject(samps)

def mutate_tempo(so: SoundObject):
    samps = lr.effects.time_stretch(so.samples, random.uniform(0.5, 2.0))
    return SoundObject(samps)

def mutate_fragment(so: SoundObject):
    fr = random.randrange(0, so.samples.size - 0.1 * sm.sound.SAMPLE_RATE)
    to = random.randrange(fr + 0.1 * sm.sound.SAMPLE_RATE , so.samples.size)
    samps = so.samples[fr:to]
    return SoundObject(samps)

def mutate_reverb(so: SoundObject):
    samps = (
        Fx()
        .reverb(
            random.uniform(0, 100),
            random.uniform(0, 100),
            random.uniform(0, 100),
            random.uniform(0, 100),
            random.uniform(0, 100)
        )
    )(so.samples)
    return SoundObject(samps)

def mutate_distortion(so: SoundObject):
    a = random.uniform(0, 1)
    samps = np.clip(so.samples, -a, a)
    return SoundObject(samps)

def mutate_chorus(so: SoundObject):
    samps = (
        Fx()
        .chorus(
            random.uniform(0, 1),
            random.uniform(0, 1),
            [[
                random.uniform(40, 60),
                random.uniform(0, 1),
                random.uniform(0.2, 0.3),
                random.uniform(1, 5),
                random.choice(["s", "t"])
            ] for _ in range(random.randrange(1, 5))]
        )
    )(so.samples)
    return SoundObject(samps)

def mutate_bandreject(so: SoundObject):
    samps = (
        Fx()
        .bandreject(
            random.uniform(20, 20e3),
            random.uniform(0.1, 2.0)
        )
    )(so.samples)
    return SoundObject(samps)

def mutate_compand(so: SoundObject):
    samps = (
        Fx()
        .compand(
            random.uniform(0.1, 1.0),
            random.uniform(0.1, 1.0),
            random.uniform(0.5, 2.0),
            random.uniform(-20, -3),
            random.uniform(-20, -3),
            random.uniform(-20, -3)
        )
    )(so.samples)
    return SoundObject(samps)

mutations = [
    mutate_bandreject,
    mutate_bandpass,
    mutate_reverse,
    mutate_reverb,
    mutate_pitch,
    mutate_tempo,
    mutate_fragment,
    mutate_distortion,
    mutate_chorus,
    #mutate_compand
]

# Fitness Functions:

def fitness_flatness(so: SoundObject, tar):
    return np.abs(tar - np.mean(lr.feature.spectral_flatness(so.samples)))

def fitness_bandwidth(so: SoundObject, tar):
    return np.abs(tar - np.mean(lr.feature.spectral_bandwidth(so.samples, sm.sound.SAMPLE_RATE)))

def fitness_target(so: SoundObject, target: SoundObject):
    nso = so.get_padded(target.duration)
    spect1 = lr.stft(nso)
    spect2 = lr.stft(target.samples)
    spect1 /= np.max(spect1)
    spect2 /= np.max(spect2)
    dif = np.abs(spect1 - spect2)
    return np.mean(dif)

def fitness_model(so: SoundObject, model):
    feats = sm.synth.get_features(so)
    return np.mean(model.predict([feats]))

fitness_components = [
    fitness_flatness,
    fitness_bandwidth,
    fitness_target,
    fitness_model
]

def fitness(so, ws, params):
    score = 0
    for w,fit,p in zip(ws, fitness_components, params):
        if w > 0: score += fit(so, p) * w
    return score
        
# Algorithm:

def evolve(lso, n_generations, elitism, mut_prob, fitness_weights, fitness_params):
    npop = len(lso)
    population = [(so, fitness(so, fitness_weights, fitness_params)) for so in lso]

    for _ in range(n_generations):
        n_child = round(npop * (1 - elitism))
        pot_parents = copy.deepcopy(population)
        childs = []

        while len(childs) < n_child:
            if len(pot_parents) < 2: pot_parents = copy.deepcopy(population)
            parent0 = random.choices(
                pot_parents,
                weights=[score for _,score in pot_parents],
                k=1
            )[0]
            pot_parents.remove(parent0)
            parent1 = random.choices(
                pot_parents,
                weights=[score for _,score in pot_parents],
                k=1
            )[0]
            pot_parents.remove(parent1)
            child = crossover(parent0[0], parent1[0])
            while random.uniform(0,1) < mut_prob:
                mut = random.choice(mutations)
                print(f"Mutating: {mut.__name__}")
                new_child = mut(child)
                if not np.isnan(new_child.samples).any():
                    child = new_child
                else:
                    print("Mutation Failed")
            try:
                child = SoundObject(lr.effects.trim(child.get_normalize_to(1.0)))
            except: continue
            fit = fitness(child, fitness_weights, fitness_params)
            if np.isnan(fit) or np.isinf(fit): continue
            childs.append((child, fit))
        
        population = sorted(population, key=lambda ind: ind[1], reverse=True)[:int(elitism * npop)] + childs
        print(max([s for _,s in population]))

    out = []
    for so,_ in population:
        ptrack, mtrack = so.track_pitch()
        pitch = lr.hz_to_midi(np.mean(ptrack))
        velocity = np.clip(np.mean(mtrack) * 127, 0, 127)
        out.append((so, pitch, velocity))
    return out
