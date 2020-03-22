import numpy as np

def mean(val, freq):
    return np.average(val, weights = freq)

def median(val, freq):
    ord = np.argsort(val)
    cdf = np.cumsum(freq[ord])
    return val[ord][np.searchsorted(cdf, cdf[-1] // 2)]

def mode(val, freq):
    return val[np.argmax(freq)]

def var(val, freq):
    avg = mean(val, freq)
    dev = freq * (val - avg) ** 2
    return dev.sum() / (freq.sum() - 1)

def std(val, freq):
    return np.sqrt(var(val, freq))