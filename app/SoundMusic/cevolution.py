# Create manipulators through evolution, but faster.
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

class CEvolution:
    # TODO: Implement source sampling

    def __init__(
        self, source, *,
        complexity=2, max_comp=5, init_n=60,
        mutation_factor=0.2, elitism=0.3, n_gens=5, ui_path="./ui/"
    ):
        self.population = []
        self.competing = (-1, -1)
        self.progress = []

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
            try:
                r = self.source.rate
                psource = SoundObject(self.source.samples[:lr.time_to_samples(5, sr=r)], r)
                self.population.append((self.make_manip().do(psource), None))
            except:
                tb.print_exc()

    def fitness(self, sound, ex_time=0.0):
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

        similarity = weights["similarity"] * sm.fitness.similarity(sound, self.source)
        amplitude_range = weights["amplitude_range"] * sm.fitness.amplitude_range(sound)
        frequency_range = weights["frequency_range"] * sm.fitness.frequency_range(sound)
        duration = weights["duration"] * sm.fitness.duration(sound, params["duration"])
        silence_ratio = weights["silence_ratio"] * sm.fitness.silence_ratio(sound, params["silence_ratio"])
        score = similarity + amplitude_range + frequency_range + duration + silence_ratio
        time_score = weights["time"] * ex_time
        return score + time_score

    @staticmethod
    def _decompose(manip):
        manip = copy.deepcopy(manip)
        out = []
        for m in manip.manipulators:
            if m in sm.compact_manipulators.compound.as_list:
                out += CEvolution._decompose(m)
        manip.manipulators = [m for m in manip.manipulators if not m in sm.compact_manipulators.compound.as_list]
        out.append(manip)
        return out

    def make_manip(self):
        classes = random.choices(sm.compact_manipulators.as_list, k=self.complexity)
        manips = [c() for c in classes]
        compound = random.choice(sm.compact_manipulators.compound.as_list)(manips)
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
        decomp = CEvolution._decompose(m1) + CEvolution._decompose(m2)
        mutation_n = int(self.mutation_factor * len(decomp))
        random.shuffle(decomp)
        decomp = decomp[:len(decomp)-mutation_n]
        decomp += [self.make_manip() for _ in range(mutation_n)]
        random.shuffle(decomp)
        decomp = decomp[:self.max_comp]
        return CEvolution._reconstruct(decomp)

    def reproduce(self):
        random.seed()
        self.population.sort(key=lambda m: m[1], reverse=True)
        elite_n = int(len(self.population) * self.elitism)
        pop_n = len(self.population)
        self.population = self.population[:elite_n]
        babies = []
        for _ in range(pop_n - elite_n):
            ms = random.choices(self.population, weights=[m[1] for m in self.population], k=1)[0]
            m = ms[0]
            #child = self.crossover(*ms)
            try:
                babies.append((self.make_manip().do(m), None))
            except:
                tb.print_exc()
        self.population += babies

    def evaluate(self):
        for i,m in enumerate(self.population):
            if m[1] == None:
                try:
                    #print("Generating:")
                    #t0 = time.time()
                    #sound = m[0].do(self.source)
                    #t1 = time.time()
                    #print("Evaluating:")
                    self.population[i] = (m[0], self.fitness(m[0], ex_time=0))
                except:
                    tb.print_exc()
                    self.population[i] = (m[0], -math.inf)
    
    def step(self):
        random.seed()
        self.evaluate()
        self.reproduce()
        scores = [m[1] for m in self.population if m[1] != None and m[1] != -math.inf and m[1] != math.nan]
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
