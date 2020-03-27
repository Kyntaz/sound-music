# Implements continuous and/or periodic functions.
import math as mt
import numpy as np

class IWave:
    def point(self, x):
        raise NotImplementedError

    def sample(self, b, e, n):
        points = np.linspace(b, e, n)
        samples = list(map(lambda x: self.point(x), points))
        return np.array(samples)

class Wave(IWave):
    def __init__(self, samples, length=1):
        self.samples = samples
        self.length = length

    def point(self, x):
        rx = (x % self.length) / self.length
        sx = rx * len(self.samples)
        bs = self.samples[mt.floor(sx)]
        ts = self.samples[mt.ceil(sx)]
        return bs + (ts-bs) * (sx%1)

class WaveFunction(IWave):
    def __init__(self, f):
        self.f = f
    
    def point(self, x):
        return self.f(x)

    @staticmethod
    def sine(f=1, a=1, ph=0):
        return WaveFunction(lambda x: mt.sin(x*f*2*mt.pi + ph)*a)

class Envelope(IWave):
    def __init__(self, points):
        self.points = points

    def point(self, x):
        xp = [p[0] for p in self.points]
        fp = [p[1] for p in self.points]
        return np.interp(x, xp, fp)

    @staticmethod
    def adsr(a=(0.2, 1), d=(0.1, 1), s=(0.5, 1), r=(0.2, 0)):
        points = [
            (0, 0),
            (a[0], a[1]),
            (d[0]+a[0], d[1]),
            (s[0]+d[0]+a[0], s[1]),
            (r[0]+s[0]+d[0]+a[0], r[1])
        ]
        return Envelope(points)