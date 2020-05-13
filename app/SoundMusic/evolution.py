# Create manipulators through evolution.
import SoundMusic as sm
import random
import librosa as lr
import numpy as np
import math
import time

def crossover(manip1, manip2):
    compound = random.choice(sm.manipulators.compound.as_list)
    return compound(random.choice([[manip1, manip2], [manip2, manip1]]))

def mutate(manip, p):
    manip.tweak(p)

def initial_pop(n):
    pop = [random.choice(sm.manipulators.as_list)() for _ in range(n)]
    for p in pop: p.tweak(1.0)
    return pop

def spec_similarity(out, source):
    spect1 = lr.amplitude_to_db(np.abs(lr.stft(source.samples)))
    spect2 = lr.amplitude_to_db(np.abs(lr.stft(out.samples)))
    spect1_trim = spect1[:,:np.shape(spect2)[1]]
    spect2_trim = spect2[:,:np.shape(spect1)[1]]
    dif_matrix = np.abs(spect1_trim - spect2_trim)
    return np.mean(dif_matrix)

def fitness(manip, source):
    weights = {
        "spec_sim": 1.0,
        "runtime": -1.0
    }
    try:
        t1 = time.time()
        out = sm.render.render_audio(manip.do([source]), pretty=True)
        t2 = time.time()
        rt = t2 - t1
        return (
            weights["spec_sim"] * spec_similarity(out, source) +
            weights["runtime"] * rt
        )
    except:
        return -math.inf

def evolve(source, pop_size, generation_n, elitism_n):
    initial_manips = initial_pop(pop_size)
    population = [(m, fitness(m, source)) for m in initial_manips]
    for g in range(generation_n):
        n_pop = []
        for _ in range(pop_size - elitism_n):
            parents = random.choices([p[0] for p in population], weights=[p[1] for p in population], k=2)
            progeny = crossover(*parents)
            mutate(progeny, (generation_n - g) / generation_n)
            f = fitness(progeny, source)
            n_pop.append((progeny, f))
        population.sort(reverse=True, key=lambda p: p[1])
        n_pop += population[:elitism_n]
        population = n_pop
        print("Population Size: ", len(population))
        print("Average Fitness: ", np.mean([p[1] for p in population]))
        print("Max Fitness: ", max([p[1] for p in population]))
    return max(population, key=lambda p: p[1])