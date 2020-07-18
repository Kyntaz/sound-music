import SoundMusic as sm
import librosa as lr
import numpy as np
from SoundMusic import SoundObject
import random
from pysndfx import AudioEffectsChain as Fx

def crossover(so1: SoundObject, so2: SoundObject) -> SoundObject:
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

    return sm.sound.join([so1.get_normalize_to(1.0), so2.get_normalize_to(1.0)])

# Mutations:

def mutate_bandpass(so: SoundObject):
    lo = random.uniform(20, 20e3)
    hi = random.uniform(lo, 20e3)
    return sm.effects.band_pass(so, lo, hi)

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
    fr = random.uniform(0, so.samples.size)
    to = random.uniform(fr, so.samples.size)
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
            [
                random.uniform(40, 60),
                random.uniform(0, 1),
                random.uniform(0.2, 0.3),
                random.uniform(1, 5),
                random.choice(["s", "t"])
            ]
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
    mutate_compand
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
        score += fit(so, p) * w
    return score
        
# Algorithm:

def evolve(lso, n_generations, elitism, fitness_weights, fitness_params):
    npop = len(lso)
    population = [(so, fitness(so, fitness_weights, fitness_params)) for so in lso]

    for _ in range(n_generations):
        n_child = round(npop * (1 - elitism))

        for _ in range(n_child):
            parents = random.choices(
                [so for so,_ in population],
                weights=[score for _,score in population],
                k=2
            )
            child = crossover(*parents)
            population.append((child, fitness(child, fitness_weights, fitness_params)))
        
        population = sorted(population, key=lambda ind: ind[1], reverse=True)[:npop]

    out = []
    for so,_ in population:
        ptrack, mtrack = so.track_pitch()
        pitch = lr.hz_to_midi(np.mean(ptrack))
        velocity = np.clip(np.mean(mtrack) * 127, 0, 127)
        out.append((so, pitch, velocity))
    return out
