# Genetic programming for synths with varying topology.
import SoundMusic as sm
import librosa as lr
import numpy as np
import random
import copy

POPULATION = 20
GENERATIONS = 100
ELITISM = 0.2
PRE_EVOLUTION = 10
MIN_COMP = 3
MAX_COMP = 15

# Synth nodes:

class Source:
    def __init__(self):
        self.ins = 0
        self.sound = None

    def set_sound(self, sound: sm.SoundObject):
        self.sound = sound

    def connect(self, ins):
        pass

    def render(self, samps):
        return self.sound.samples[:samps]

    def get_ins(self):
        return []

class SinOsc:
    def __init__(self):
        self.ins = 3
        self.freq = None
        self.amp = None
        self.phase = None

    def connect(self, ins):
        self.freq = ins[0]
        self.amp = ins[1]
        self.phase = ins[2]

    def render(self, samps):
        f = self.freq.render(samps)
        a = self.amp.render(samps)
        p = self.phase.render(samps)
        t = sm.waves.tspan(samps / sm.sound.SAMPLE_RATE)
        return sm.waves.sin(t, f, a, p)

    def get_ins(self):
        return [self.freq, self.amp, self.phase]

class SqOsc:
    def __init__(self):
        self.ins = 3
        self.freq = None
        self.amp = None

    def connect(self, ins):
        self.freq = ins[0]
        self.amp = ins[1]
        self.phase = ins[2]

    def render(self, samps):
        f = self.freq.render(samps)
        a = self.amp.render(samps)
        p = self.phase.render(samps)
        t = sm.waves.tspan(samps / sm.sound.SAMPLE_RATE)
        return sm.waves.square(t, f, a, p)

    def get_ins(self):
        return [self.freq, self.amp, self.phase]

class TriOsc:
    def __init__(self):
        self.ins = 3
        self.freq = None
        self.amp = None

    def connect(self, ins):
        self.freq = ins[0]
        self.amp = ins[1]
        self.phase = ins[2]

    def render(self, samps):
        f = self.freq.render(samps)
        a = self.amp.render(samps)
        p = self.phase.render(samps)
        t = sm.waves.tspan(samps / sm.sound.SAMPLE_RATE)
        return sm.waves.triangle(t, f, a, p)

    def get_ins(self):
        return [self.freq, self.amp, self.phase]

class SawOsc:
    def __init__(self):
        self.ins = 3
        self.freq = None
        self.amp = None

    def connect(self, ins):
        self.freq = ins[0]
        self.amp = ins[1]
        self.phase = ins[2]

    def render(self, samps):
        f = self.freq.render(samps)
        a = self.amp.render(samps)
        p = self.phase.render(samps)
        t = sm.waves.tspan(samps / sm.sound.SAMPLE_RATE)
        return sm.waves.saw(t, f, a, p)

    def get_ins(self):
        return [self.freq, self.amp, self.phase]

class Constant:
    def __init__(self):
        self.ins = 0
        self.val = random.uniform(0, 10e3)

    def setVal(self, val):
        self.val = val

    def connect(self, ins):
        pass

    def render(self, samps):
        return np.asfortranarray([self.val] * samps)

    def get_ins(self):
        return []


class Filter:
    def __init__(self):
        self.ins = 3
        self.low = None
        self.high = None
        self.sig = None

    def connect(self, ins):
        self.low = ins[0]
        self.high = ins[1]
        self.sig = ins[2]

    def render(self, samps):
        lo = np.average(np.abs(self.low.render(samps)))
        hi = np.average(np.abs(self.high.render(samps)))
        return sm.effects.band_pass(sm.SoundObject(self.sig.render(samps)), lo, hi).samples[:samps]

    def get_ins(self):
        return [self.low, self.high, self.sig]

class Add:
    def __init__(self):
        self.ins = 3
        self.sig1 = None
        self.sig2 = None

    def connect(self, ins):
        self.sig1 = ins[0]
        self.sig2 = ins[1]

    def render(self, samps):
        return self.sig1.render(samps) + self.sig2.render(samps)

    def get_ins(self):
        return [self.sig1, self.sig2]

class Mult:
    def __init__(self):
        self.ins = 3
        self.sig1 = None
        self.sig2 = None

    def connect(self, ins):
        self.sig1 = ins[0]
        self.sig2 = ins[1]

    def render(self, samps):
        return self.sig1.render(samps) * self.sig2.render(samps)

    def get_ins(self):
        return [self.sig1, self.sig2]

class Output:
    def __init__(self):
        self.ins = 1
        self.sig = None

    def connect(self, ins):
        self.sig = ins[0]

    def render(self, samps):
        return self.sig.render(samps)

    def get_ins(self):
        return [self.sig]

node_types = [SinOsc, SqOsc, TriOsc, SqOsc, Filter, Add, Mult, Constant]

# Synth

class TopologySynth:
    def __init__(self):
        self.source = Source()
        self.out = Output()
        self.out.connect([self.source])
        self.nodes = [self.source, self.out]

    def gen(self, so: sm.SoundObject):
        self.source.set_sound(so)
        return sm.SoundObject(self.out.render(np.size(so.samples)))

    def mutate_add(self):
        node = random.choice(node_types)()
        ins = []
        for _ in range(node.ins):
            inode = random.choice(self.nodes)
            while isinstance(inode, Output):
                inode = random.choice(self.nodes)
            ins.append(inode)
        node.connect(ins)
        onode = random.choice(self.nodes)
        while isinstance(onode, Source) or isinstance(onode, Constant):
            onode = random.choice(self.nodes)
        outs = onode.get_ins()
        outs[random.randint(0, len(outs) - 1)] = node
        onode.connect(outs)
        self.nodes.append(node)

    def mutate_remove(self):
        node = random.choice(self.nodes)
        while isinstance(node, Source) or isinstance(node, Output):
            node = random.choice(self.nodes)
        self.nodes.remove(node)
        for onode in self.nodes:
            ins = onode.get_ins()
            for i, inn in enumerate(ins):
                if inn == node:
                    inode = random.choice(self.nodes)
                    while isinstance(inode, Output) or inode == onode:
                        inode = random.choice(self.nodes)
                    ins[i] = inode
                    onode.connect(ins)

    def mutate(self):
        healthy = False
        while not healthy:
            try:
                random.seed()
                if len(self.nodes) >= MAX_COMP: self.mutate_remove()
                elif len(self.nodes) <= MIN_COMP: self.mutate_add()
                else:
                    if random.randint(0,1) == 0:
                        self.mutate_remove()
                    else:
                        self.mutate_add()
                self.gen(sm.SoundObject(sm.waves.sin(sm.waves.tspan(1), 440, 1, 0)))
                healthy = True
            except KeyboardInterrupt:
                exit()
            except:
                healthy = False

    def dbg(self):
        print("===")
        for i,node in enumerate(self.nodes):
            for onode in node.get_ins():
                j = self.nodes.index(onode)
                print(f"{j} -> {i}")
        print("===")
            

# GA

def evolve(lso, fit):
    pre_pop = [TopologySynth() for _ in range(POPULATION)]
    for _ in range(PRE_EVOLUTION):
        for ind in pre_pop: ind.mutate()
    pop = []
    for ind in pre_pop:
        try: score = sm.synth.fast_fitness(ind, lso, fit)
        except:
            score = - np.inf
        pop.append((ind, score))

    for g in range(GENERATIONS):
        print(f"Generation {g}")
        pop = sorted(pop, key=lambda e: e[1], reverse=True)
        elite = int(ELITISM * len(pop))
        pop = pop[elite:]
        parents = copy.copy(pop)

        while len(pop) < POPULATION:
            if len(parents) < 1:
                parents = copy.copy(pop)
            parent = random.choices(parents, weights=[sc for _,sc in parents], k=1)[0]
            parents.remove(parent)

            healthy = False
            while not healthy:
                child = copy.deepcopy(parent[0])
                child.mutate()

                try:
                    score = sm.synth.fast_fitness(ind, lso, fit)
                    healthy = True
                except:
                    healthy = False
            
            pop.append((child, score))
        
    pop = sorted(pop, key=lambda e: e[1], reverse=True)
    pop[0][0].dbg()
    return [ind for ind,_ in pop][:sm.synth.POPULATION]
