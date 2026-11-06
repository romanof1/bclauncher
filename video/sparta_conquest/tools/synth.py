"""Музыка и звуковой дизайн: «Спарта — завоевание и три сословия».
Дорийский лад на ре (D E F G A B C), 100 BPM, такт 2.4 с.
Инструменты: лира (Karplus-Strong), авлос (пила + вибрато + дыхание), рамочный барабан, тайко, рог.
События синхронизации берутся из audio/events.json (выгружает tools/events.js).
python3 tools/synth.py → audio/mix.wav
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _synthlib import *  # noqa
from scipy.io import wavfile

DUR = 43.2
N = int(DUR * SR)
BEAT = 0.6
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = json.load(open(os.path.join(ROOT, 'audio', 'events.json')))
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))


def aulos(m, dur, vib=5.5, bright=2600):
    n = int(dur * SR)
    t = tt(n)
    f = hz(m) * (1 + 0.006 * np.sin(2 * np.pi * vib * t) * np.minimum(1, t / 0.25))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(ph * k) / k * (1 if k % 2 else 0.6) for k in range(1, 12))
    x = bp(x, 350, bright)
    x += bp(rng.standard_normal(n), 1500, 5000) * 0.04
    e = np.minimum(1, t / 0.04) * np.clip((dur - t) / 0.08, 0, 1)
    return x * e * 0.5


def frame_drum(accent=1.0):
    n = int(0.45 * SR)
    t = tt(n)
    body = np.sin(2 * np.pi * np.cumsum(95 + 60 * np.exp(-t * 40)) / SR) * np.exp(-t * 12)
    slap = bp(rng.standard_normal(n), 700, 4000) * np.exp(-t * 45)
    return (body * 0.8 + slap * 0.5 * accent) * 0.7


def horn(notes, dur, att=0.12):
    s = pad(notes, dur, att=att, rel=0.4, cutoff=1300, det=0.003)
    return np.tanh(s * 2.2) * 0.6


def stone_hit(size=1.0):
    n = int(1.4 * SR)
    t = tt(n)
    boom = np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-t * 14)) / SR) * np.exp(-t * 3.5)
    return np.tanh(boom * 1.4 + np.pad(crunch(0.6, size), (0, n - int(0.6 * SR))) * 0.6) * 0.9


def blip(f=900):
    n = int(0.12 * SR)
    t = tt(n)
    return np.sin(2 * np.pi * np.cumsum(f + 900 * t / 0.12) / SR) * np.exp(-t * 25) * 0.5


def pop():
    n = int(0.25 * SR)
    t = tt(n)
    return (bp(rng.standard_normal(n), 1500, 7000) * np.exp(-t * 60) + np.sin(2 * np.pi * 300 * t) * np.exp(-t * 30) * 0.5) * 0.8


def step():
    n = int(0.15 * SR)
    t = tt(n)
    return lp(rng.standard_normal(n), 500) * np.exp(-t * 40) * 1.2


D3, E3, F3, G3, A3, B3, C4 = 50, 52, 53, 55, 57, 59, 60
D4, E4, F4, G4, A4, B4, C5, D5, E5, F5, G5, A5 = 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81
D2, A2 = 38, 45

# ---------- S1: «герой» 0–3.0 (светлая лира + авлос), стоп на зачёркивании ----------
put(music, 0.0, pad([D3, A3], 3.0, att=0.6, rel=0.3, cutoff=900), 0.25)
arp = [D4, F4, A4, D5, C5, A4, F4, A4]
for k in range(10):
    put(music, k * BEAT / 2, ks(hz(arp[k % 8]), 0.8, 0.6, 0.997), 0.28, 0.3 * np.sin(k))
mel = [(0.6, A4, 0.55), (1.2, D5, 0.55), (1.8, E5, 0.3), (2.1, F5, 0.55)]
for t0, m, d in mel:
    put(music, t0, aulos(m, d), 0.32, -0.15)
n = int(0.32 * SR)
tg = tt(n)
put(sfx, 2.78, np.sin(2 * np.pi * np.cumsum(700 * np.exp(-tg * 6)) / SR) * np.exp(-tg * 5) * 0.5, 0.35)  # «пшик» героизма
# ---------- S1→S2a: война, марш 3.6–10.8 ----------
put(music, 3.6, taiko(1.8), 1.0)
put(music, 3.6, horn([D2 + 12, A2 + 12, D3], 2.2, att=0.2), 0.55)
put(music, 3.6, pad([D2, A2], 7.2, att=0.4, rel=0.6, cutoff=380), 0.45)
for b in range(int((10.8 - 3.6) / (BEAT / 2))):
    t0 = 3.6 + b * BEAT / 2
    put(music, t0, frame_drum(1.0 if b % 2 == 0 else 0.5), 0.45 if b % 4 == 0 else 0.25, -0.2)
    if b % 4 == 0:
        put(music, t0, taiko(0.8), 0.55)
put(music, 7.2, horn([D3, A3, D4], 1.6), 0.4)
march = [(6.0, D5, .3), (6.3, D5, .3), (6.6, E5, .3), (6.9, F5, .6), (7.5, E5, .3), (7.8, D5, .3), (8.1, C5, .6), (8.7, D5, .3), (9.0, E5, .3), (9.3, F5, .3), (9.6, G5, .6), (10.2, A5, .55)]
for t0, m, d in march:
    put(music, t0, aulos(m, d), 0.3, 0.15)
put(sfx, 5.68, whoosh(0.62, 2400, 400), 0.4)
for t0, d in [(7.4, 1.5), (7.75, 1.25), (8.05, 1.15)]:
    put(sfx, t0, whoosh(d, 300, 2500), 0.22, 0.3)
put(sfx, 9.72, ks(hz(A5), 0.6, 0.9, 0.995), 0.35)
put(sfx, 9.72, frame_drum(), 0.4)
put(sfx, 10.5, whoosh(0.45, 500, 5000), 0.35)
# ---------- S2b: долина, покорение 10.8–15.6 ----------
for b in range(int((12.0 - 10.8) / BEAT)):
    put(music, 10.8 + b * BEAT, frame_drum(0.6), 0.3)
put(music, 12.2, taiko(1.9), 1.0)
put(music, 12.2, horn([D2 + 12, F3, A3], 1.8, att=0.05), 0.55)
put(music, 12.8, pad([D3, F3, A3], 2.6, att=0.6, rel=0.8, cutoff=900), 0.3)
sad = [(13.2, A4, .6), (13.8, G4, .6), (14.4, F4, .6), (15.0, E4, .45)]
for t0, m, d in sad:
    put(music, t0, aulos(m, d, vib=4.5, bright=1800), 0.28, -0.1)
# ---------- S3: три плиты 15.6–20.4 ----------
n = int(1.3 * SR)
tr = tt(n)
put(music, 15.3, whoosh(1.3, 200, 1800) * 0.8, 0.35)
chords = [(16.6, [D2 + 12, A2 + 12, D3, F3]), (17.2, [G3 - 12, D3, G3, B3]), (17.9, [A2 + 12, E3, A3, C4])]
for t0, ch in chords:
    put(music, t0, horn(ch, 0.7 if t0 < 17.9 else 1.5, att=0.02), 0.5)
put(music, 18.85, pad([D3, A3, D4, F4], 1.6, att=0.1, rel=0.9, cutoff=1400), 0.35)
for b in range(int((20.4 - 18.0) / (BEAT / 2))):
    put(music, 18.0 + b * BEAT / 2, frame_drum(0.7 if b % 2 == 0 else 0.4), 0.28)
# ---------- S4: спартиаты — фанфара 20.4–25.2 ----------
put(music, 20.4, pad([D3, A3, D4], 4.8, att=0.4, rel=0.6, cutoff=1300), 0.3)
fan = [(20.85, D4, .3), (21.15, A4, .3), (21.45, D5, .6), (22.05, F5, .3), (22.35, E5, .3), (22.65, D5, .9)]
for t0, m, d in fan:
    put(music, t0, horn([m - 12, m], d, att=0.03), 0.35)
for k in range(int((25.2 - 20.4) / (BEAT / 2))):
    put(music, 20.4 + k * BEAT / 2, ks(hz([D4, A4, F4, A4, E4, A4, F4, A4][k % 8]), 0.7, 0.55, 0.996), 0.2, 0.35)
for b in range(int((25.2 - 20.4) / BEAT)):
    put(music, 20.4 + b * BEAT, frame_drum(0.5), 0.25 if b % 2 else 0.4)
# ---------- S5: периэки — мастерская 25.2–36.0 ----------
put(music, 25.2, pad([D3, G3, B3 - 12 + 12], 5.8, att=0.4, rel=0.6, cutoff=1100), 0.25)
ost = [D4, F4, G4, A4, B4, A4, G4, F4]
for k in range(int((33.4 - 25.2) / (BEAT / 2))):
    put(music, 25.2 + k * BEAT / 2, ks(hz(ost[k % 8]), 0.6, 0.5, 0.995), 0.22, -0.3)
for b in range(int((33.4 - 25.2) / BEAT)):
    put(music, 25.2 + b * BEAT, frame_drum(0.6), 0.3)
    if b % 4 == 0:
        put(music, 25.2 + b * BEAT, taiko(0.7), 0.35)
put(music, 31.0, pad([D3, F3, A3, C4], 2.4, att=0.2, rel=0.6, cutoff=1500), 0.3)
put(music, 33.4, pad([D3, A3 - 1, E4 - 1], 2.6, att=0.3, rel=0.8, cutoff=900, det=0.01), 0.32)  # «без голоса» — напряжённо
put(music, 34.5, aulos(A4, 0.35, bright=1500), 0.3)
put(music, 34.85, aulos(F4, 0.7, vib=3.5, bright=1300), 0.3)
# ---------- S6: илоты — тяжело 36.0–43.2 ----------
put(music, 36.0, pad([D2, A2, D3], 4.2, att=0.5, rel=1.0, cutoff=320), 0.55)
for b in range(6):
    put(music, 36.0 + b * BEAT * 2, taiko(1.2), 0.6 if b == 0 else 0.42)
nc = int(4.0 * SR)
tc = tt(nc)
creak = bp(rng.standard_normal(nc), 90, 400) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * tc)) * np.sin(np.pi * tc / 4.0)
put(sfx, 36.1, creak, 0.25)
put(music, 39.6, pad([D3, A3, D4, F4, E4 + 12], 3.6, att=0.6, rel=2.4, cutoff=1600), 0.38)
for k, m in enumerate([D4, F4, A4, D5, E5, F5, A5]):
    put(music, 39.9 + k * 0.15, ks(hz(m), 1.6, 0.6, 0.998), 0.24, -0.4 + k * 0.13)
put(music, 39.9, taiko(1.0), 0.45)
put(music, 40.55, aulos(D5, 1.9, vib=4.5, bright=2200), 0.25)

# ---------- SFX по событиям анимации ----------
for e in EV:
    k, t0 = e['k'], e['t']
    if k == 'slab':
        put(sfx, t0, stone_hit(1.0 + 0.2 * e['n']), 0.75)
        put(sfx, t0 - 0.38, whoosh(0.38, 400, 2200), 0.25)
    elif k == 'jump':
        put(sfx, t0, whoosh(0.35, 500, 2600), 0.12, 0.2)
    elif k == 'land':
        put(sfx, t0, step(), 0.55)
    elif k == 'hammer':
        put(sfx, t0, metal(880, 0.45, 0.6), 0.22, -0.35)
    elif k == 'coinUp':
        put(sfx, t0, blip(1400), 0.12, 0.2)
    elif k == 'coin':
        put(sfx, t0, metal(2200, 0.35, 0.4), 0.18, 0.1)
    elif k == 'helmet':
        put(sfx, t0, metal(520, 0.6, 0.6), 0.2, 0.25)
    elif k == 'bubble':
        put(sfx, t0, blip(700), 0.3, 0.1)
    elif k == 'pop':
        put(sfx, t0, pop(), 0.45, -0.2)
    elif k == 'step':
        put(sfx, t0, step(), 0.22, -0.4)
    elif k == 'kneel':
        put(sfx, t0, lp(rng.standard_normal(int(0.2 * SR)), 900) * env(int(0.2 * SR), 0.01, 0.07), 0.12, 0.3)
# ветер долины
nw = int(DUR * SR)
put(sfx, 0, bp(rng.standard_normal(nw), 300, 1200) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * tt(nw))), 0.025)


def reverb(x, sec=2.0, wet=0.25):
    n = int(sec * SR)
    ir = rng.standard_normal((n, 2)) * np.exp(-tt(n) * 6.5 / sec)[:, None]
    ir = np.stack([lp(ir[:, 0], 5000), lp(ir[:, 1], 5000)], 1)
    ir /= np.sqrt((ir ** 2).sum(0))
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - wet) + y * wet * 2.2


mixd = reverb(music, 2.2, 0.28) * 0.9 + reverb(sfx, 1.0, 0.14)
mixd = np.stack([hp(mixd[:, c], 35) for c in range(2)], 1)
mixd = mixd / np.max(np.abs(mixd)) * 1.25
mixd = np.tanh(mixd) * 0.89
f_in = np.minimum(1, tt(N) / 0.01)
f_out = np.clip((DUR - tt(N)) / 1.2, 0, 1) ** 0.7
mixd *= (f_in * f_out)[:, None]
out = os.path.join(ROOT, 'audio', 'mix.wav')
wavfile.write(out, SR, (mixd * 2 ** 31 * 0.999).astype(np.int32))
print('written', out, 'rms dB', 20 * np.log10(np.sqrt(np.mean(mixd ** 2))))
