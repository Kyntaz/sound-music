# Interactive evolution algorithm.
import SoundMusic as sm
import random
import time
import copy
import os.path

class UiEvolution:

    def __init__(self, source, rep_cycle=10, complexity=5, init_n=30, mutation_factor=0.1, elitism=0.3, ui_path="./ui/"):
        self.population = []
        self.reproduction_timer = 0
        self.competing = (-1, -1)
        self.files = ("", "")

        self.source = source
        self.reproduction_cycle = rep_cycle
        self.complexity = complexity
        self.init_n = init_n
        self.mutation_factor = mutation_factor
        self.elitism = elitism
        self.ui_path = ui_path
        
    def start(self):
        self.population = []
        for _ in range(self.init_n):
            self.population.append((self.make_manip(), 0, ""))
        for _ in range(5):
            self.reproduce()
        self.compete()
        return self.files

    def compete(self):
        m1 = None
        m2 = None
        while m1 == m2:
            m1, s1, a1 = random.choices(self.population, weights=[1 / (m[1] + 1) for m in self.population])[0]
            m2, s2, a2 = random.choices(self.population, weights=[m[1] for m in self.population])[0]
        
        i1 = self.population.index((m1, s1, a1))
        i2 = self.population.index((m2, s2, a2))

        if a1 == "":
            out1 = sm.render.render_audio(m1.do([self.source]), fade=3.0, pretty=True)
            path_1 = f"temp/audio1-{time.time()}.wav"
            p1 = os.path.join(self.ui_path, path_1)
            out1.write(p1)
            self.population[i1] = (m1, s1, path_1)

        if a2 == "":
            out2 = sm.render.render_audio(m2.do([self.source]), fade=3.0, pretty=True)
            path_2 = f"temp/audio2-{time.time()}.wav"
            p2 = os.path.join(self.ui_path, path_2)
            out2.write(p2)
            self.population[i2] = (m2, s2, path_2)

        self.competing = (i1, i2)
        self.files = (self.population[i1][2], self.population[i2][2])

    @staticmethod
    def _decompose(manip):
        manip = copy.deepcopy(manip)
        out = []
        for m in manip.manipulators:
            if m in sm.manipulators.compound.as_list:
                out += UiEvolution._decompose(m)
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
        decomp = UiEvolution._decompose(m1) + UiEvolution._decompose(m2)
        mutation_n = int(self.mutation_factor * len(decomp))
        random.shuffle(decomp)
        decomp = decomp[:len(decomp)-mutation_n]
        decomp += [self.make_manip() for _ in range(mutation_n)]
        return UiEvolution._reconstruct(decomp)

    def reproduce(self):
        random.seed()
        self.population.sort(key=lambda m: m[1], reverse=True)
        elite_n = int(len(self.population) * self.elitism)
        pop_n = len(self.population)
        self.population = self.population[:elite_n]
        for _ in range(pop_n - elite_n):
            ms = random.choices(self.population, weights=[m[1] for m in self.population], k=2)
            ms = [m[0] for m in ms]
            child = self.crossover(*ms)
            self.population.append((child, 0, ""))
    
    def step(self, w):
        random.seed()
        winner = self.population[self.competing[w]]
        loser = self.population[self.competing[(w+1)%2]]
        self.population[self.competing[w]] = (winner[0], max(winner[1], loser[1] + 1), winner[2])
        self.reproduction_timer += 1
        if self.reproduction_timer >= self.reproduction_cycle:
            self.reproduction_timer = 0
            self.reproduce()
        self.compete()
        return self.files

    def render_best(self):
        best = max(self.population, key=lambda m: m[1])
        print(best)
        if best[2] != "":
            return best[2]
        out = best[0].do([self.source])
        out_r = sm.render.render_audio(out, pretty=True, fade=3)
        path = f"temp/audio-{time.time()}.wav"
        p = os.path.join(self.ui_path, path)
        out_r.write(p)
        return path
