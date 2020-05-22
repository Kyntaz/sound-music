# Create manipulators through evolution.
import SoundMusic as sm
from SoundMusic.sound import SoundObject
import random
import time
import copy
import os.path
import numpy as np
import math
import traceback as tb
import librosa as lr

class Evolution:
    # TODO: Implement source sampling

    def __init__(
        self, source, *,
        complexity=3, max_comp=5, init_n=60,
        mutation_factor=0.2, elitism=0.3, n_gens=5, ui_path="./ui/"
    ):
        self.population = []
        self.competing = (-1, -1)
        self.progress = []
        self.source_samples = []

        self.source = source
        self.complexity = complexity
        self.max_comp = max_comp
        self.init_n = init_n
        self.mutation_factor = mutation_factor
        self.elitism = elitism
        self.ui_path = ui_path
        self.n_gens = n_gens
        
    def start(self):
        self.population = []
        for _ in range(self.init_n):
            self.population.append((self.make_manip(), None))
        
        # Generate source samples:
        samp_dur = lr.time_to_samples(1.0, self.source.rate)
        source_mid = int(self.source.samples.size / 2.0)
        self.source_samples = [
            SoundObject(self.source.samples[:samp_dur], self.source.rate),
            SoundObject(self.source.samples[source_mid:source_mid+samp_dur], self.source.rate),
            SoundObject(self.source.samples[-samp_dur:], self.source.rate),
        ]
        for s in self.source_samples:
            print(s.duration())

    def fitness(self, sounds, ex_time=0.0):
        weights = {
            "similarity": -1.0,
            "amplitude_range": 1.0,
            "frequency_range": 1.0,
            "duration": 1.0,
            "silence_ratio": 1.0,
            "time": 0.0
        }

        params = {
            "climax_position": 2.0 / 3.0,
            "duration": 150.0,
            "silence_ratio": 0.0
        }

        score = 0
        for g,o in zip(sounds, self.source_samples):
            similarity = weights["similarity"] * sm.fitness.similarity(g, o)
            amplitude_range = weights["amplitude_range"] * sm.fitness.amplitude_range(g)
            frequency_range = weights["frequency_range"] * sm.fitness.frequency_range(g)
            duration = weights["duration"] * sm.fitness.duration(g, params["duration"])
            silence_ratio = weights["silence_ratio"] * sm.fitness.silence_ratio(g, params["silence_ratio"])
            score += similarity + amplitude_range + frequency_range + duration + silence_ratio
        time_score = weights["time"] * ex_time
        return score / len(self.source_samples) + time_score

    @staticmethod
    def _decompose(manip):
        manip = copy.deepcopy(manip)
        out = []
        for m in manip.manipulators:
            if m in sm.manipulators.compound.as_list:
                out += Evolution._decompose(m)
        manip.manipulators = [m for m in manip.manipulators if not m in sm.manipulators.compound.as_list]
        out.append(manip)
        return out

    def make_manip(self):
        classes = random.choices(sm.manipulators.as_list, k=self.complexity)
        manips = [c() for c in classes]
        compound = random.choice(sm.manipulators.compound.as_list)(manips)
        compound.tweak(1.0)
        return compound

    @staticmethod
    def _reconstruct(manips):
        while len(manips) > 1:
            m1 = random.choice(manips)
            manips.remove(m1)
            m2 = random.choice(manips)
            manips.remove(m2)
            m1.manipulators.insert(int(round(random.uniform(0, len(m1.manipulators)))), m2)
            manips.append(m1)
        return manips[0]

    def crossover(self, m1, m2):
        decomp = Evolution._decompose(m1) + Evolution._decompose(m2)
        mutation_n = int(self.mutation_factor * len(decomp))
        random.shuffle(decomp)
        decomp = decomp[:len(decomp)-mutation_n]
        decomp += [self.make_manip() for _ in range(mutation_n)]
        random.shuffle(decomp)
        decomp = decomp[:self.max_comp]
        return Evolution._reconstruct(decomp)

    def reproduce(self):
        random.seed()
        self.population.sort(key=lambda m: m[1], reverse=True)
        elite_n = int(len(self.population) * self.elitism)
        pop_n = len(self.population)
        self.population = self.population[:elite_n]
        babies = []
        for _ in range(pop_n - elite_n):
            ms = random.choices(self.population, weights=[m[1] for m in self.population], k=2)
            ms = [m[0] for m in ms]
            child = self.crossover(*ms)
            babies.append((child, None))
        self.population += babies

    def evaluate(self):
        for i,m in enumerate(self.population):
            if m[1] == None:
                try:
                    print("Generating:")
                    t0 = time.time()
                    sounds = [sm.render.render_audio(m[0].do([o])) for o in self.source_samples]
                    t1 = time.time()
                    print("Evaluating:")
                    self.population[i] = (m[0], self.fitness(sounds, ex_time=t1-t0))
                except:
                    tb.print_exc()
                    self.population[i] = (m[0], -math.inf)
    
    def step(self):
        random.seed()
        self.evaluate()
        self.reproduce()
        scores = [m[1] for m in self.population if m[1] != None and m[1] != -math.inf]
        v_max = np.max(scores)
        v_mean = np.mean(scores)
        print(f"Max score: {v_max}")
        print(f"Mean score: {v_mean}")
        self.progress.append((v_max, v_mean))

    def run(self):
        self.start()
        for i in range(self.n_gens):
            print(f"Generation {i}")
            self.step()
        self.evaluate()
        print("Done")

    def render_best(self):
        best = max(self.population, key=lambda m: m[1])
        out = best[0].do([self.source])
        out_r = sm.render.render_audio(out, pretty=True, fade=3)
        path = f"temp/audio-{time.time()}.wav"
        p = os.path.join(self.ui_path, path)
        out_r.write(p)
        return path
