import SoundMusic as sm
from SoundMusic import SoundObject
import numpy as np
import librosa as lr
import librosa.display
import random
import copy

RESOLUTION = 10
MIN_FREQ = 20
MAX_FREQ = 1e3
MAX_LOW_FREQ = 0.2
MIN_SAMP_LEN = 0.2
MAX_SAMP_LEN = 5.0
TRIALS = 3

POPULATION = 3
GENERATIONS = 3
ELITISM = 0.5
MUTATION_RATE = 5
MUTATION_VAR = 5
SAMPLE_DURATION = 10

MAX_DRONE_DUR = 20
MIN_DRONE_DUR = 5
SWELL = 0.1

class Drone:
    def __init__(self, freqs, phases, amps, amp_freqs, amp_phases):
        self.freqs = freqs
        self.phases = phases
        self.amps = amps
        self.amp_freqs = amp_freqs
        self.amp_phases = amp_phases

    def play(self, dur):
        times = sm.waves.tspan(dur)
        waves = []

        for freq, phase, amp, amp_freq, amp_phase in zip(
            self.freqs, self.phases, self.amps, self.amp_freqs, self.amp_phases
        ):
            wave = sm.waves.sin(times, freq, amp, phase)
            mod = sm.waves.sin(times, amp_freq, 1.0, amp_phase)
            wave *= mod
            waves.append(SoundObject(wave))
        
        return sm.sound.join(waves)

class SampleDrone:
    def __init__(self, so, starts, durs, low_freqs, high_freqs, amps, amp_freqs, amp_phases):
        self.so = so
        self.starts = starts
        self.durs = durs
        self.low_freqs = low_freqs
        self.high_freqs = high_freqs
        self.amps = amps
        self.amp_freqs = amp_freqs
        self.amp_phases = amp_phases

    def play(self, dur):
        times = sm.waves.tspan(dur)
        waves = []

        for start, wdur, lf, hf, amp, amp_freq, amp_phase in zip(
            self.starts, self.durs, self.low_freqs, self.high_freqs, self.amps, self.amp_freqs, self.amp_phases
        ):
            ss = lr.time_to_samples(start, sm.sound.SAMPLE_RATE)
            es = lr.time_to_samples(start + wdur, sm.sound.SAMPLE_RATE)
            es = min(es, self.so.samples.size - 1)
            samps = self.so.samples[ss:es]
            if samps.size <= 0:
                continue
            if hf < lf:
                hf, lf = lf, hf
            if es - ss > 0.1 * sm.sound.SAMPLE_RATE:
                samps = sm.effects.band_pass(SoundObject(samps), lf, hf).samples
            peak = np.max(np.abs(samps))
            if peak > 0.0:
                samps /= peak
            samp_dur = lr.samples_to_time(samps.size, sm.sound.SAMPLE_RATE)
            wave = np.interp(
                times, 
                np.linspace(0, samp_dur, samps.size),
                samps,
                period=samp_dur
            ) * amp
            mod = sm.waves.sin(times, amp_freq, 1.0, amp_phase)
            wave *= mod
            waves.append(SoundObject(wave))

        return sm.sound.join(waves)

def make_random_drone():
    return Drone(
        freqs=[random.uniform(MIN_FREQ, MAX_FREQ) for _ in range(RESOLUTION)],
        phases=[random.uniform(0, 2*np.pi) for _ in range(RESOLUTION)],
        amps=[random.uniform(0, 1) for _ in range(RESOLUTION)],
        amp_freqs=[random.uniform(0, MAX_LOW_FREQ) for _ in range(RESOLUTION)],
        amp_phases=[random.uniform(0, 2*np.pi) for _ in range(RESOLUTION)]
    )

def make_random_sdrone(so: SoundObject):
    return SampleDrone(
        so=so,
        starts=[random.uniform(0, so.duration) for _ in range(RESOLUTION)],
        durs=[random.uniform(MIN_SAMP_LEN, MAX_SAMP_LEN) for _ in range(RESOLUTION)],
        low_freqs=[random.uniform(20, 2e4) for _ in range(RESOLUTION)],
        high_freqs=[random.uniform(20, 2e4) for _ in range(RESOLUTION)],
        amps=[random.uniform(0, 1) for _ in range(RESOLUTION)],
        amp_freqs=[random.uniform(0, MAX_LOW_FREQ) for _ in range(RESOLUTION)],
        amp_phases=[random.uniform(0, 2*np.pi) for _ in range(RESOLUTION)]
    )

def loss(drone: Drone, so: SoundObject):
    out = 0
    for _ in range(TRIALS):
        drone_wave = drone.play(SAMPLE_DURATION)
        st = random.uniform(0, so.duration - SAMPLE_DURATION)
        et = st + SAMPLE_DURATION
        ss = lr.time_to_samples(st, sm.sound.SAMPLE_RATE)
        es = lr.time_to_samples(et, sm.sound.SAMPLE_RATE)
        stft1 = lr.stft(so.samples[ss:es])
        stft2 = lr.stft(drone_wave.samples)
        out += np.mean(np.abs(stft1 - stft2))
    return out / TRIALS

def crossover(d1: Drone, d2: Drone):
    return Drone(
        freqs=[random.choice([o1, o2]) for o1,o2 in zip(d1.freqs, d2.freqs)],
        phases=[random.choice([o1, o2]) for o1,o2 in zip(d1.phases, d2.phases)],
        amps=[random.choice([o1, o2]) for o1,o2 in zip(d1.amps, d2.amps)],
        amp_freqs=[random.choice([o1, o2]) for o1,o2 in zip(d1.amp_freqs, d2.amp_freqs)],
        amp_phases=[random.choice([o1, o2]) for o1,o2 in zip(d1.amp_phases, d2.amp_phases)]
    )

def scrossover(d1: SampleDrone, d2: SampleDrone):
    return SampleDrone(
        so=d1.so,
        starts=[random.choice([o1, o2]) for o1,o2 in zip(d1.starts, d2.starts)],
        durs=[random.choice([o1, o2]) for o1,o2 in zip(d1.durs, d2.durs)],
        low_freqs=[random.choice([o1, o2]) for o1,o2 in zip(d1.low_freqs, d2.low_freqs)],
        high_freqs=[random.choice([o1, o2]) for o1,o2 in zip(d1.high_freqs, d2.high_freqs)],
        amps=[random.choice([o1, o2]) for o1,o2 in zip(d1.amps, d2.amps)],
        amp_freqs=[random.choice([o1, o2]) for o1,o2 in zip(d1.amp_freqs, d2.amp_freqs)],
        amp_phases=[random.choice([o1, o2]) for o1,o2 in zip(d1.amp_phases, d2.amp_phases)]
    )

def mutate(drone: Drone):
    idx = random.randint(0, len(drone.freqs) - 1)
    drone.freqs[idx] = random.uniform(MIN_FREQ, MAX_FREQ)
    drone.phases[idx] = random.uniform(0, 2*np.pi)
    drone.amps[idx] = random.uniform(0, 1)
    drone.amp_freqs[idx] = random.uniform(0, MAX_LOW_FREQ)
    drone.amp_phases[idx] = random.uniform(0, 2*np.pi)

def smutate(drone: SampleDrone):
    idx = random.randint(0, len(drone.starts) - 1)
    drone.starts[idx] = random.uniform(0, drone.so.duration)
    drone.durs[idx] = random.uniform(MIN_SAMP_LEN, MAX_SAMP_LEN)
    drone.high_freqs[idx] = random.uniform(20, 2e4)
    drone.low_freqs[idx] = random.uniform(20, 2e4)
    drone.amps[idx] = random.uniform(0, 1)
    drone.amp_freqs[idx] = random.uniform(0, MAX_LOW_FREQ)
    drone.amp_phases[idx] = random.uniform(0, 2*np.pi)

def join_drones(drones, dur, amp):
    times = sm.waves.tspan(dur)
    waves = []
    for drone in drones:
        so = drone.play(dur)
        mod_freq = random.uniform(1 / MAX_DRONE_DUR, 1 / MIN_DRONE_DUR)
        mod_phase = random.uniform(0, 2*np.pi)
        mod = sm.waves.sin(times, mod_freq, amp / 2, mod_phase) + (amp / 2)
        so = SoundObject(so.samples * mod)
        waves.append(so)
    return sm.sound.join(waves)

def evolve(so, dur, amp):
    population = []
    for _ in range(POPULATION):
        drone = make_random_drone()
        lval = loss(drone, so)
        population.append([drone, lval])

    for _ in range(GENERATIONS):
        elite = int(ELITISM * POPULATION)
        new_population = sorted(population, key=lambda ind: ind[1])[:elite]
        weights = [1 / ind[1] for ind in population]

        while len(new_population) < POPULATION:
            parents = random.choices([ind for ind, _ in population], weights=weights, k=2)
            child = crossover(*parents)
            n_mutations = max(random.normalvariate(MUTATION_RATE, MUTATION_VAR), 0)

            for _ in range(int(n_mutations)): mutate(child)

            lval = loss(child, so)
            new_population.append([child, lval])

        population = new_population

    return join_drones([ind[0] for ind in population], dur, amp)

def sevolve(so, dur, amp):
    population = []
    for _ in range(POPULATION):
        drone = make_random_sdrone(so)
        lval = loss(drone, so)
        population.append([drone, lval])

    for _ in range(GENERATIONS):
        elite = int(ELITISM * POPULATION)
        new_population = sorted(population, key=lambda ind: ind[1])[:elite]
        weights = [1 / ind[1] for ind in population]

        while len(new_population) < POPULATION:
            parents = random.choices([ind for ind, _ in population], weights=weights, k=2)
            child = scrossover(*parents)
            n_mutations = max(random.normalvariate(MUTATION_RATE, MUTATION_VAR), 0)

            for _ in range(int(n_mutations)): smutate(child)

            lval = loss(child, so)
            new_population.append([child, lval])

        population = new_population
        print(min(fit for _,fit in population))

    return join_drones([ind[0] for ind in population], dur, amp)

def side_chain(point_durs_int, so: SoundObject):
    times = sm.waves.tspan(so.duration)
    curve = np.ones_like(so.samples)

    for start, end, intens in point_durs_int:
        p = (start + end) / 2
        w = end - start
        bump = sm.waves.bump(times, intens, p, w)
        curve -= bump

    curve = np.maximum(curve, 0.0)
    f = int(SWELL * so.duration * sm.sound.SAMPLE_RATE)
    l = curve.size
    curve = np.concatenate([
        np.linspace(0, 1, f),
        np.ones(l - 2 * f),
        np.linspace(1, 0, f)
    ]) * curve
    return SoundObject(so.samples * curve)


