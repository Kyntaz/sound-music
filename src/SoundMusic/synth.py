import random
import librosa as lr
import numpy as np
import scipy as sp
import SoundMusic as sm
from SoundMusic import SoundObject
from SoundMusic.sound import SAMPLE_RATE
import copy
import sklearn as skl

# Settings for the Evolutionary Algorithm:
GENERATIONS = 3
POPULATION = 3
ELITISM = 0.5
AVG_MUTATIONS = 3
VAR_MUTATIONS = 5
CROSS_ALPHA = 0.3

# Settings for SVM evaluation of fitness.
SAMPLES = 3
FAST_CYCLE = 10

class SynthParam:
    def __init__(self, rand_f):
        self.rand_f = rand_f
        self.randomize()
    
    def randomize(self):
        self.v = self.rand_f()
    
    def copy(self):
        return SynthParam(self.rand_f)

    @staticmethod
    def pint(lo, hi):
        return SynthParam(lambda: random.randint(lo, hi))

    @staticmethod
    def pfloat(lo, hi):
        return SynthParam(lambda: random.uniform(lo, hi))

    @staticmethod
    def plist(l):
        return SynthParam(lambda: random.choice(l))

class ISynth:
    def __init__(self):
        self.params = []

    def mutate(self):
        random.choice(self.params).randomize()

    @property
    def genome(self):
        return [param.v for param in self.params]

    @classmethod
    def from_genome(cls, genome):
        synth = cls()
        for param, val in zip(synth.params, genome):
            param.v = val
        return synth

    def gen(self, so: SoundObject):
        return so

class SpectralGrainsSynth(ISynth):
    def __init__(self):
        self.in_density_mean = SynthParam.pfloat(10, 50)
        self.in_density_var = SynthParam.pfloat(5, 20)
        self.out_density_mean = SynthParam.pfloat(10, 50)
        self.out_density_var = SynthParam.pfloat(5, 20)
        self.width_mean = SynthParam.pfloat(0.01, 1.0)
        self.width_var = SynthParam.pfloat(0.01, 1.0)
        self.freq_var = SynthParam.pfloat(0, 0.3)

        self.params = [
            self.in_density_mean,
            self.in_density_var,
            self.out_density_mean,
            self.out_density_var,
            self.width_mean,
            self.width_var,
            self.freq_var
        ]
    
    def gen(self, so: SoundObject):
        idm = self.in_density_mean.v
        idv = self.in_density_var.v
        odm = self.out_density_mean.v
        odv = self.out_density_var.v
        wm = self.width_mean.v
        wv = self.width_var.v
        fv = self.freq_var.v

        stft = lr.stft(so.samples)
        stft_r = np.real(stft)
        stft_i = np.imag(stft)
        interp_r = sp.interpolate.interp2d(
            np.linspace(0, so.duration, np.shape(stft_r)[1]),
            np.linspace(0, 1 , np.shape(stft_r)[0]),
            stft_r
        )
        interp_i = sp.interpolate.interp2d(
            np.linspace(0, so.duration, np.shape(stft_i)[1]),
            np.linspace(0, 1 , np.shape(stft_i)[0]),
            stft_i
        )
        canvas_r = np.zeros_like(stft_r)
        canvas_i = np.zeros_like(stft_i)

        n_grains = int(odm * so.duration)
        for _ in range(n_grains):
            in_dur = np.clip(1 / random.normalvariate(idm, idv), 0.03, so.duration)
            out_dur = np.clip(1 / random.normalvariate(odm, odv), 0.03, so.duration)
            width = np.clip(min(random.normalvariate(wm, wv), 1.0), 0.01, 1.0)

            in_start = random.uniform(0, so.duration - in_dur)
            in_end = in_start + in_dur
            out_start = random.uniform(0, so.duration - out_dur)
            out_end = out_start + out_dur
            out_start_frame = lr.time_to_frames(out_start, sr=SAMPLE_RATE)
            out_end_frame = lr.time_to_frames(out_end, sr=SAMPLE_RATE)
            n_frames = out_end_frame - out_start_frame

            width_start = random.uniform(0, 1.0 - width)
            out_width_start = np.clip(random.normalvariate(width_start, fv), 0, 1.0 - width)
            out_width_end = out_width_start + width
            out_width_start_bin = int(out_width_start * np.shape(canvas_r)[0])
            out_width_end_bin = int(out_width_end * np.shape(canvas_r)[0])
            width_end = width_start + width
            width_bins = out_width_end_bin - out_width_start_bin

            grid_dur = np.linspace(in_start, in_end, n_frames)
            grid_width = np.linspace(width_start, width_end, width_bins)

            canvas_r[
                out_width_start_bin:out_width_end_bin,
                out_start_frame:out_end_frame
            ] += interp_r(grid_dur, grid_width)
            canvas_i[
                out_width_start_bin:out_width_end_bin,
                out_start_frame:out_end_frame
            ] += interp_i(grid_dur, grid_width)
        
        canvas = canvas_r + canvas_i * 1j
        samps = lr.istft(canvas)
        return SoundObject(np.concatenate([
            samps,
            np.zeros(so.samples.size - samps.size
        )]))

class GranularSynth(ISynth):
    def __init__(self):
        self.in_density_mean = SynthParam.pfloat(10, 500)
        self.in_density_var = SynthParam.pfloat(5, 100)
        self.out_density_mean = SynthParam.pfloat(10, 500)
        self.out_density_var = SynthParam.pfloat(5, 100)

        self.params = [
            self.in_density_mean,
            self.in_density_var,
            self.out_density_mean,
            self.out_density_var
        ]

    def gen(self, so: SoundObject):
        idm = self.in_density_mean.v
        idv = self.in_density_var.v
        odm = self.out_density_mean.v
        odv = self.out_density_var.v

        samps = so.samples
        canvas = np.zeros_like(samps)

        n_grains = int(odm * so.duration)
        for _ in range(n_grains):
            in_dur = np.clip(
                lr.time_to_samples(1 / random.normalvariate(idm, idv), sr=SAMPLE_RATE),
                1, samps.size
            )
            out_dur = np.clip(
                lr.time_to_samples(1 / random.normalvariate(odm, odv), sr=SAMPLE_RATE),
                1, canvas.size
            )

            in_start = random.randint(0, samps.size - in_dur)
            in_end = in_start + in_dur

            out_start = random.randint(0, canvas.size - out_dur)
            out_end = out_start + out_dur

            in_points = np.linspace(in_start, in_end, out_dur)
            canvas[out_start:out_end] += np.interp(
                in_points,
                np.linspace(0, samps.size, samps.size),
                samps
            )

        return SoundObject(canvas)

class PhaseDistortionSynth(ISynth):
    def __init__(self):
        self.shape = SynthParam.plist([
            sm.waves.sin,
            sm.waves.square,
            sm.waves.saw,
            sm.waves.triangle
        ])
        self.freq = SynthParam.pfloat(0.1, 100.0)
        self.amp = SynthParam.pfloat(0.1, 50.0)
        self.phase = SynthParam.pfloat(0.0, 2 * np.pi)

        self.params = [
            self.shape,
            self.freq,
            self.amp,
            self.phase
        ]

    def gen(self, so: SoundObject):
        shape = self.shape.v
        freq = self.freq.v
        amp = self.amp.v
        phase = self.phase.v

        times = sm.waves.tspan(so.duration)
        distortion = shape(times, freq, amp, phase)
        out = np.interp(times + distortion, times, so.samples, period=so.duration)

        return SoundObject(out)

class FrequencyModulationSynth(ISynth):
    def __init__(self):
        self.shape = SynthParam.plist([
            sm.waves.sin,
            sm.waves.square,
            sm.waves.saw,
            sm.waves.triangle
        ])
        self.phase = SynthParam.pfloat(0, 2 * np.pi)

        self.params = [
            self.shape,
            self.phase
        ]

    def gen(self, so: SoundObject):
        shape = self.shape.v
        phase = self.phase.v

        pitch, mag = so.track_pitch()
        times = sm.waves.tspan(so.duration)
        pitch = np.interp(times, np.linspace(0, so.duration, pitch.size), pitch)
        mag = np.interp(times, np.linspace(0, so.duration, mag.size), mag) * 0.1

        out = shape(times, pitch, mag, phase)
        return SoundObject(out)

class AdditiveSynth(ISynth):
    def __init__(self):
        self.shape = SynthParam.plist([
            sm.waves.sin,
            sm.waves.square,
            sm.waves.saw,
            sm.waves.triangle
        ])
        self.n_layers = SynthParam.pint(1, 25)

        self.params = [
            self.shape,
            self.n_layers
        ]

    def gen(self, so: SoundObject):
        shape = self.shape.v
        n_layers = self.n_layers.v

        stft = lr.stft(so.samples)
        spect = np.abs(stft)
        phasem = np.angle(stft)
        fprofile = np.mean(spect, axis=1)
        phase_mean = np.mean(phasem, axis=1)
        top_bins = np.argsort(fprofile)[-n_layers:]
        freqs = lr.fft_frequencies(sr=SAMPLE_RATE)

        canvas = np.zeros_like(so.samples)
        times = sm.waves.tspan(so.duration)

        for bi in top_bins:
            ph = phasem[bi,:]
            amp = spect[bi,:]
            fr = freqs[bi]
            ph = phase_mean[bi]
            amp = np.interp(times, np.linspace(0, so.duration, amp.size), amp)
            wave = shape(times, fr, amp, ph)
            canvas += wave

        return SoundObject(canvas)

class WaveSynth:
    def __init__(self):
        self.freq = SynthParam.pfloat(0.1, 880)
        self.params = [self.freq]

    def gen(self, so: SoundObject):
        dur = so.duration
        ns = np.size(so.samples)
        idxs = np.linspace(0, ns * dur * self.freq.v, ns)
        samps = np.interp(idxs, np.linspace(0, ns, ns), so.samples, period=ns)
        return SoundObject(samps)

class SoundSynth(ISynth):
    def __init__(self):
        self.synths = [
            SpectralGrainsSynth(),
            GranularSynth(),
            GranularSynth(),
            PhaseDistortionSynth(),
            FrequencyModulationSynth(),
            FrequencyModulationSynth(),
            AdditiveSynth(),
            AdditiveSynth(),
            WaveSynth(),
            WaveSynth(),
            WaveSynth()
        ]
        self.volumes = [SynthParam.pfloat(-1,1) for _ in self.synths]
        self.mod_shapes = [SynthParam.plist([
            sm.waves.sin,
            sm.waves.square,
            sm.waves.triangle,
            sm.waves.saw
        ]) for _ in self.synths]
        self.mod_amps = [SynthParam.pfloat(0,1) for _ in self.synths]
        self.mod_freqs = [SynthParam.pfloat(0,10) for _ in self.synths]
        self.mod_phases = [SynthParam.pfloat(0, 2 * np.pi) for _ in self.synths]

        self.params = (
            self.volumes +
            self.mod_shapes +
            self.mod_amps +
            self.mod_freqs +
            self.mod_phases +
            sum([s.params for s in self.synths], [])
        )

    def gen(self, so: SoundObject):
        times = sm.waves.tspan(so.duration)
        return sm.sound.join([
            SoundObject(synth.gen(so).samples * (vol.v + shape.v(times,fr.v,amp.v,ph.v))) for
            synth,vol,shape,amp,fr,ph in zip(
                self.synths,
                self.volumes,
                self.mod_shapes,
                self.mod_amps,
                self.mod_freqs,
                self.mod_phases
            )
        ])

def crossover(synth1, synth2):
    geno1 = synth1.genome
    geno2 = synth2.genome
    geno_c = [random.choice([g1,g2]) if not isinstance(g1, float)
        else (CROSS_ALPHA * g1 + (1 - CROSS_ALPHA) * g2) for
        g1,g2 in zip(geno1, geno2)]
    return type(synth1).from_genome(geno_c)

def fitness(synth, lso):
    while True:
        try:
            so = synth.gen(random.choice(lso))
            so.play()
            score = float(input("score > "))
            sm.sound.stop()
            break
        except ValueError:
            sm.sound.stop()
            print("Invalid Score...")
    return (score, so)

def get_features(so: SoundObject):
    feature = lr.feature.mfcc(so.get_padded(sm.extraction.MAX_LEN), SAMPLE_RATE)
    feature = feature.flatten()
    return feature

def get_model(user_inputs):
    model = skl.svm.SVR()
    features = []
    targets = []
    for so, fit in user_inputs:
        targets.append(fit)
        features.append(get_features(so))
    model.fit(np.stack(features, axis=0), targets)
    return model

def fast_fitness(synth, lso, model):
    features = []
    for tso in lso:
        so = synth.gen(tso)
        features.append(get_features(so))
    return np.mean(model.predict(features))

def target_fitness(synth, lso, target):
    diff = 0
    for tso in lso:
        so = synth.gen(tso)
        f1 = so.get_f0()
        f2 = target.get_f0()
        fratio = f2 / f1
        samps = lr.resample(target.samples, sm.sound.SAMPLE_RATE, int(sm.sound.SAMPLE_RATE * fratio))
        samps = SoundObject(samps).get_padded(so.duration)
        fft1 = np.abs(lr.stft(samps))
        fft2 = np.abs(lr.stft(so.samples))
        diff += np.mean(np.abs(fft1 - fft2))
    return - diff / len(lso)

def evolve(synth_class, lso):
    population = []
    user_inputs = []
    model = None
    for _ in range(POPULATION):
        synth = synth_class()
        fit, so = fitness(synth, lso)
        population.append([synth, fit])
        user_inputs.append([so, fit])

    for ig in range(GENERATIONS):
        elite = int(POPULATION * ELITISM)
        new_population = sorted(population, key=lambda ss: ss[1])[-elite:]

        possible_parents = []
        while len(new_population) < POPULATION:
            if len(possible_parents) < 2:
                possible_parents = copy.copy(population)
            
            parent1 = random.choices(
                possible_parents,
                weights=[ss[1] for ss in possible_parents],
                k=1
            )[0]
            possible_parents.remove(parent1)

            parent2 = random.choices(
                possible_parents,
                weights=[ss[1] for ss in possible_parents],
                k=1
            )[0]
            possible_parents.remove(parent2)
            
            child = crossover(parent1[0], parent2[0])
            n_mutations = max(int(random.normalvariate(AVG_MUTATIONS, VAR_MUTATIONS)), 0)
            for _ in range(n_mutations): child.mutate()
            if ig % FAST_CYCLE == 0:
                fit, so = fitness(child, lso)
                new_population.append([child, fit])
                user_inputs.append([so, fit])
            else:
                fit = fast_fitness(child, lso, model)
                new_population.append([child, fit])
        
        if ig % FAST_CYCLE == 0:
            model = get_model(user_inputs)
            
        population = new_population
    
    return ([synth for synth,_ in population], model)

def fast_evolve(synth_class, lso, model):
    population = []
    if isinstance(model, SoundObject): currfit = target_fitness
    else: currfit = fast_fitness

    for _ in range(POPULATION):
        synth = synth_class()
        fit = currfit(synth, lso, model)
        population.append([synth, fit])

    for _ in range(GENERATIONS):
        elite = int(POPULATION * ELITISM)
        new_population = sorted(population, key=lambda ss: ss[1])[-elite:]

        possible_parents = []
        while len(new_population) < POPULATION:
            if len(possible_parents) < 2:
                possible_parents = copy.copy(population)
            
            ws = np.array([ss[1] for ss in possible_parents])
            ws += min(np.min(ws), 0)
            parent1 = random.choices(
                possible_parents,
                weights=ws,
                k=1
            )[0]
            possible_parents.remove(parent1)

            ws = np.array([ss[1] for ss in possible_parents])
            ws += min(np.min(ws), 0)
            parent2 = random.choices(
                possible_parents,
                weights=[ss[1] for ss in possible_parents],
                k=1
            )[0]
            possible_parents.remove(parent2)
            
            child = crossover(parent1[0], parent2[0])
            n_mutations = max(int(random.normalvariate(AVG_MUTATIONS, VAR_MUTATIONS)), 0)
            for _ in range(n_mutations): child.mutate()

            fit = currfit(child, lso, model)
            new_population.append([child, fit])
            
        print(max(fit for _,fit in new_population))
        population = new_population
    
    return [synth for synth,_ in sorted(population, key=lambda ss: ss[1], reverse=True)]

def make_synths(synth_class):
    return [synth_class() for _ in range(POPULATION)]