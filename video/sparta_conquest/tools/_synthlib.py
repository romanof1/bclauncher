"""Общие синтез-функции (из первого ролика серии)."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000
rng = np.random.default_rng(11)
def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(n):
    return np.arange(n) / SR


def lp(x, f, o=2):
    return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)


def bp(x, a, b, o=2):
    return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)


def env(n, a=0.005, d=0.3, curve=1.0):
    t = tt(n)
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d * curve)
    return e


def put(buf, t0, sig, gain=1.0, pan=0.0):
    N = len(buf)
    i = int(round(t0 * SR))
    if i >= N:
        return
    if i < 0:
        sig = sig[-i:]
        i = 0
    sig = sig[: N - i]
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * gain * l * 1.414
    buf[i:i + len(sig), 1] += sig * gain * r * 1.414


def saw(f, n, det=0.0):
    t = tt(n)
    out = np.zeros(n)
    for k in range(1, 40):
        if f * k > 12000:
            break
        out += np.sin(2 * np.pi * f * k * t * (1 + det)) / k
    return out * 0.6


def ks(f, dur, bright=0.5, damp=0.996):
    """Karplus-Strong: лира / щипок"""
    n = int(dur * SR)
    p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p)
    buf = lp(buf, 1500 + 6000 * bright) if p > 20 else buf
    out = np.zeros(n)
    for i in range(n):
        j = i % p
        v = buf[j]
        out[i] = v
        buf[j] = damp * 0.5 * (v + buf[(j + 1) % p])
    return out * env(n, 0.002, dur * 0.45)


# ---------------- инструменты ----------------
def taiko(big=1.0):
    n = int(1.6 * SR)
    t = tt(n)
    f = 46 + 90 * np.exp(-t * 18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * (3.2 / big))
    skin = lp(rng.standard_normal(n), 900) * np.exp(-t * 30) * 0.5
    return np.tanh((body + skin) * 1.6) * 0.8


def kick():
    n = int(0.5 * SR)
    t = tt(n)
    f = 50 + 120 * np.exp(-t * 35)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 2) * 0.8


def snare():
    n = int(0.35 * SR)
    t = tt(n)
    return (bp(rng.standard_normal(n), 900, 6000) * np.exp(-t * 18) * 0.6 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.4)


def click(f=3200, d=0.012):
    n = int(0.05 * SR)
    t = tt(n)
    return bp(rng.standard_normal(n), f * 0.7, min(f * 1.4, 20000)) * np.exp(-t / d)


def metal(f0=420, dur=1.4, bright=1.0):
    n = int(dur * SR)
    t = tt(n)
    ratios = [1, 2.76, 5.40, 8.93, 13.34]
    out = np.zeros(n)
    for k, r in enumerate(ratios):
        out += np.sin(2 * np.pi * f0 * r * t + k) * np.exp(-t * (3 + k * 2.5) / bright) / (k + 1)
    out += hp(rng.standard_normal(n), 3000) * np.exp(-t * 60) * 0.4
    return out * 0.5


def gong(f0=98, dur=5.0):
    n = int(dur * SR)
    t = tt(n)
    out = np.zeros(n)
    for k, (r, d) in enumerate([(1, 1.2), (1.48, 0.9), (2.02, 0.7), (2.74, 0.5), (3.6, 0.4), (4.9, 0.3)]):
        out += np.sin(2 * np.pi * f0 * r * t * (1 + 0.002 * np.sin(t * 3 + k))) * np.exp(-t * d) / (k + 1)
    return out * np.minimum(1, t / 0.01) * 0.5


def whoosh(dur, f0=300, f1=4000, up=True):
    n = int(dur * SR)
    t = tt(n)
    x = rng.standard_normal(n)
    out = np.zeros(n)
    seg = 512
    for s in range(0, n, seg):
        u = s / n
        fc = f0 * (f1 / f0) ** (u if up else 1 - u)
        out[s:s + seg] = bp(x[max(0, s - 2048):s + seg], fc * 0.6, min(fc * 1.6, 20000))[-len(x[s:s + seg]):]
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    return out * e * 0.7


def crunch(dur=0.7, size=1.0):
    n = int(dur * SR)
    t = tt(n)
    grains = np.zeros(n)
    for k in range(int(30 * size)):
        i = int(rng.uniform(0, 0.5) * n * (rng.uniform() ** 1.5))
        g = rng.standard_normal(int(0.02 * SR)) * np.exp(-np.arange(int(0.02 * SR)) / (0.004 * SR))
        grains[i:i + len(g)] += g[: n - i] * rng.uniform(0.3, 1)
    low = np.sin(2 * np.pi * np.cumsum(70 * size ** -0.3 + 60 * np.exp(-t * 20)) / SR) * np.exp(-t * 7)
    return np.tanh(bp(grains, 300, 7000) * 0.7 + low * 0.9) * 0.8


def pad(notes, dur, att=0.8, rel=1.0, cutoff=1800, det=0.004):
    n = int(dur * SR)
    out = np.zeros(n)
    for m in notes:
        f = hz(m)
        out += saw(f, n, det) + saw(f, n, -det)
    out = lp(out, cutoff, 2)
    t = tt(n)
    e = np.minimum(1, t / att) * np.minimum(1, (dur - t) / rel)
    return out * np.clip(e, 0, 1) / max(1, len(notes))


def sine_chord(notes, dur, att=0.6, rel=1.2):
    n = int(dur * SR)
    t = tt(n)
    out = sum(np.sin(2 * np.pi * hz(m) * t + k) * (1 + 0.3 * np.sin(t * (4 + k))) for k, m in enumerate(notes))
    e = np.clip(np.minimum(t / att, (dur - t) / rel), 0, 1)
    return out * e / len(notes)


