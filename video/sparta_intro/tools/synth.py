"""Музыка и звуковой дизайн для ролика «Спарта — вступление».
100 BPM, ре минор, такт 2.4 с. Все события привязаны к таймлайну index.html
(часть берётся из audio/events.json, его выгружает tools/events.js).
python3 tools/synth.py  → audio/mix.wav (48 кГц, стерео, 24 бит)
"""
import json, os
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
DUR = 41.4
N = int(DUR * SR)
BEAT = 0.6
rng = np.random.default_rng(7)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EV = json.load(open(os.path.join(ROOT, 'audio', 'events.json')))

music = np.zeros((N, 2))
sfx = np.zeros((N, 2))


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


# ================= МУЗЫКА =================
D2, A2, D3, F3, A3, D4, E4, F4, G4, A4, C5, D5, E5, F5, A5 = 38, 45, 50, 53, 57, 62, 64, 65, 67, 69, 72, 74, 76, 77, 81

# S1 0–7.2: дрон, тайко, остинато
put(music, 0.0, pad([D2, A2, D3], 7.6, att=1.5, rel=0.6, cutoff=700), 0.55)
for b in range(12):
    t = b * BEAT
    if b % 2 == 0:
        put(music, t, taiko(0.8), 0.55 if b % 4 else 0.75)
put(music, 0.6, taiko(1.3), 0.9)            # «300»
put(music, 3.0, taiko(1.6), 1.0)            # «НЕСМЕТНОЙ»
put(music, 3.0, gong(73, 3.0), 0.22)
for k in range(int((7.2 - 1.2) / (BEAT / 2))):
    t = 1.2 + k * BEAT / 2
    m = [D2, D2, A2, D2, F3 - 12, D2, A2, D3][k % 8]
    put(music, t, ks(hz(m + 12), 0.5, 0.35, 0.993), 0.32 * (0.6 + 0.4 * min(1, k / 10)), -0.25)
for k in range(8):                           # тремоло перед «застывшим»
    put(music, 6.0 + k * 0.15, taiko(0.5), 0.15 + k * 0.04)

# 7.2 застывание: высокий «каменный» аккорд, всё стихает
put(music, 7.2, sine_chord([D5, F5, A5, E5 + 12], 3.4, att=0.15, rel=1.6), 0.18)
put(music, 7.2, pad([D2, A2], 2.2, att=0.05, rel=1.4, cutoff=300), 0.35)
# 9.0–13.0: возвращается пульс, торжественно (храм, «СПАРТЕ»)
put(music, 9.0, pad([D3, A3, D4, F4], 4.4, att=0.3, rel=0.8, cutoff=1400), 0.38)
put(music, 9.0, pad([D2, A2], 4.4, att=0.2, rel=0.8, cutoff=400), 0.5)
for b in range(int((13.2 - 9.0) / BEAT)):
    t = 9.0 + b * BEAT
    put(music, t, taiko(0.9 if b % 4 == 0 else 0.6), 0.65 if b % 4 == 0 else 0.4)
put(music, 9.3, gong(110, 2.5), 0.18)       # «СПАРТЕ»
for k in range(int((13.0 - 9.0) / (BEAT / 2))):
    m = [D3, A2 + 12, F3, A3, D4, A3, F3, A2 + 12][k % 8]
    put(music, 9.0 + k * BEAT / 2, ks(hz(m + 12), 0.6, 0.55, 0.995), 0.22, 0.3)

# S3 13.2–18.6: лира-арпеджио, мягкий бой; на «солдатах» — полный удар
arp = [D4, F4, A4, D5, A4, F4, E4, A4]
for k in range(int((18.4 - 13.2) / (BEAT / 2))):
    t = 13.2 + k * BEAT / 2
    put(music, t, ks(hz(arp[k % 8]), 0.9, 0.6, 0.997), 0.3, 0.35 * np.sin(k))
put(music, 13.2, pad([D3, A3, F4], 3.0, att=0.6, rel=0.6, cutoff=900), 0.32)
put(music, 15.0, pad([A2 + 12, E4, G4 - 12 + 12], 1.3, att=0.3, rel=0.4, cutoff=900), 0.3)  # «не люди»: подвешенный
for b in range(int((16.2 - 13.2) / BEAT)):
    if b % 2 == 0:
        put(music, 13.2 + b * BEAT, taiko(0.6), 0.32)
put(music, 16.2, taiko(1.8), 1.0)            # «А СОЛДАТЫ»
put(music, 16.2, pad([D2, A2, D3, F3, A3], 2.4, att=0.03, rel=1.2, cutoff=1600), 0.5)
for b in range(4):
    put(music, 16.8 + b * BEAT, taiko(0.8), 0.55)

# S4 18.6–26.4: часы, напряжение, диссонанс, вихрь
for k in range(int((26.2 - 18.6) / (BEAT / 2))):
    t = 18.6 + k * BEAT / 2
    put(music, t, click(2600 if k % 2 else 3600, 0.01), 0.22)
put(music, 18.6, pad([D3, A3, D4], 2.9, att=0.6, rel=0.5, cutoff=1100), 0.3)       # «идеальным» — чистая квинта
put(music, 21.4, pad([D2 + 12, D3 + 3, A3 - 1, E4 - 1], 2.4, att=0.08, rel=0.6, cutoff=1300, det=0.012), 0.42)  # «жестокий»
put(music, 21.95, taiko(1.4), 0.85)
for b in range(4):
    put(music, 22.2 + b * BEAT, kick(), 0.35)
# вихрь змеи: нисходящее глиссандо
n = int(2.8 * SR)
tg = tt(n)
fgl = 880 * 2 ** (-tg * 1.0)
gl = np.sin(2 * np.pi * np.cumsum(fgl) / SR) * np.sin(np.pi * tg / 2.8) ** 2
put(music, 23.5, gl, 0.12, 0.2)
put(music, 23.6, pad([D2, D3 + 1, A3 - 1], 2.8, att=1.0, rel=0.3, cutoff=800, det=0.015), 0.38)
for k in range(10):
    put(music, 25.2 + k * 0.12, taiko(0.4), 0.08 + k * 0.035)  # разгон к склейке

# S5 26.4–34.2: машина — грув
put(music, 26.4, taiko(1.5), 0.85)
put(music, 26.4, pad([D2, A2], 1.6, att=0.02, rel=1.0, cutoff=300), 0.5)
for b in range(int((34.2 - 27.6) / BEAT)):
    t = 27.6 + b * BEAT
    put(music, t, kick(), 0.7)
    if b % 2 == 1 and t >= 28.8:
        put(music, t, snare(), 0.35, 0.1)
bass = [D2, D2, D3, D2, F3 - 12, D2, C5 - 36, D2]
for k in range(int((34.2 - 27.6) / (BEAT / 2))):
    t = 27.6 + k * BEAT / 2
    s = lp(saw(hz(bass[k % 8]), int(0.28 * SR)), 500) * env(int(0.28 * SR), 0.004, 0.12)
    put(music, t, s, 0.55)
for t0, ch in [(28.8, [D3, F3, A3, D4]), (31.2, [C5 - 24, F3, A3, C5 - 12]), (33.6, [A2, E4 - 12, A3, C5 - 12])]:
    st = pad(ch, 0.9, att=0.02, rel=0.6, cutoff=2400)
    put(music, t0, st, 0.5)
    put(music, t0, taiko(1.2), 0.7)
put(music, 30.55, taiko(1.6), 0.8)          # «МАШИНУ»
put(music, 30.55, metal(140, 1.5, 0.8), 0.22)

# 34.2 обрыв. 34.6–36.6 почти тишина: низкий гул и ветер
put(music, 34.6, pad([D2 - 12, D2], 2.2, att=0.6, rel=0.8, cutoff=200), 0.4)
nw = int(4.0 * SR)
wind = bp(rng.standard_normal(nw), 300, 1400) * np.sin(np.pi * tt(nw) / 4.0) ** 2 * (0.6 + 0.4 * np.sin(tt(nw) * 1.3))
put(sfx, 34.8, wind, 0.08)

# 36.6 «ОДНО»: удар, гонг, суббас
n = int(3.5 * SR)
t3 = tt(n)
sub = np.sin(2 * np.pi * np.cumsum(30 + 40 * np.exp(-t3 * 3)) / SR) * np.exp(-t3 * 1.1)
put(music, 36.6, sub, 0.8)
put(music, 36.6, taiko(2.2), 1.0)
put(music, 36.6, gong(73.4, 5.0), 0.42)
# 38.0 сердцебиение, 38.8 финальный аккорд
for t0 in (38.0, 38.32):
    put(music, t0, kick(), 0.4)
fin = pad([D2, A2, D3, F3, A3, E4], 2.9, att=0.25, rel=2.0, cutoff=1500)
put(music, 38.5, fin, 0.5)
put(music, 38.75, sine_chord([D4, A4, E5, F5], 2.65, att=0.5, rel=1.8), 0.16)
put(music, 38.75, taiko(1.4), 0.6)

# ================= SFX =================
for e in EV:
    if e['k'] == 'clang':
        i = EV.index(e)
        put(sfx, e['t'], metal(520 + (i % 3) * 37, 0.9), 0.16, -0.6 + 1.2 * ((i % 11) / 10))
    elif e['k'] == 'tick':
        put(sfx, e['t'], click(1800, 0.02), 0.25, 0.4)
    elif e['k'] == 'break':
        sz = e['size'] / 400
        put(sfx, e['t'], crunch(0.9, sz), 0.55, 0.3 if sz < 1 else -0.2)
# шорох пыли на S1, ветер
nd = int(7 * SR)
put(sfx, 0.0, bp(rng.standard_normal(nd), 400, 2000) * np.sin(np.pi * tt(nd) / 7) * 0.5, 0.06)
# застывание: треск камня
put(sfx, 7.2, crunch(1.2, 0.6), 0.35, 0.0)
put(sfx, 7.2, whoosh(0.5, 3000, 300, True), 0.25)
# колонны: проезд / подъём
put(sfx, 7.7, whoosh(1.1, 200, 1800), 0.35, -0.4)
put(sfx, 8.4, taiko(0.5), 0.25)              # фронтон сел
# шторка-колонна
put(sfx, 12.9, whoosh(0.75, 150, 2500), 0.6, 0.5)
# «не люди» — зачёркивание
put(sfx, 15.75, bp(rng.standard_normal(int(0.35 * SR)), 2000, 7000) * env(int(0.35 * SR), 0.02, 0.15), 0.18, -0.3)
# подъём камеры (складывание)
put(sfx, 18.25, whoosh(0.7, 2500, 400), 0.4, 0.0)
# лаборатория: линейки
put(sfx, 21.45, whoosh(0.9, 3000, 6000), 0.12, 0.2)
# змея: шелест
put(sfx, 23.5, whoosh(2.8, 600, 3000), 0.22, 0.3)
# склейка в точку
put(sfx, 26.0, whoosh(0.45, 400, 5000), 0.35)
# свиток
put(sfx, 26.85, whoosh(1.0, 1500, 5000), 0.18, 0.4)
# щелчки шестерён — плотность от скорости машины
tk = 27.9
while tk < 34.2:
    sp = 1.75 * (0.5 - 0.5 * np.cos(np.pi * min(1, max(0, (tk - 27.85) / 1.55))))
    put(sfx, tk, click(1500, 0.008), 0.16, 0.5)
    tk += max(0.06, 0.6 / max(sp, 0.25) / 2.2)
# заклинивание: скрежет
n = int(0.6 * SR)
tsq = tt(n)
scr = np.sin(2 * np.pi * np.cumsum(900 + 400 * np.sin(tsq * 70)) / SR) * np.exp(-tsq * 4)
put(sfx, 34.2, scr * 0.5 + metal(300, 0.6) * 0.5, 0.35, 0.3)
put(sfx, 34.2, taiko(1.0), 0.6)
# падения обломков и законодателя
for k in range(12):
    put(sfx, 34.85 + k * 0.09 + rng.uniform(0, 0.05), taiko(0.35), 0.35 * (1 - k / 14), rng.uniform(-0.4, 0.6))
put(sfx, 35.15, taiko(0.6), 0.45, -0.6)
# буквы «РАЗВАЛИЛАСЬ» сыпятся
for k in range(12):
    put(sfx, 34.55 + k * 0.05, click(900, 0.02), 0.15, -0.5)
# щит катится и ложится, как монета
n = int(1.05 * SR)
tr_ = tt(n)
roll = bp(rng.standard_normal(n), 120, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(9 - 6 * tr_) / SR)) * np.minimum(1, tr_ / 0.2) * (1 - tr_ / 1.05)
put(sfx, 37.9, roll, 0.3, 0.6)
put(sfx, 38.95, metal(330, 1.6), 0.3, 0.2)
tw, k = 39.55, 0
while tw < 40.6:
    put(sfx, tw, metal(330 + k * 3, 0.5, 0.5), 0.2 * np.exp(-(tw - 39.55) * 1.8), 0.2)
    per = 0.12 / (1 + (tw - 39.55) * 2.2)
    tw += max(0.025, per)
    k += 1

# ================= сведение =================
def reverb(x, sec=2.2, wet=0.25):
    n = int(sec * SR)
    ir = rng.standard_normal((n, 2)) * np.exp(-tt(n) * 6.5 / sec)[:, None]
    ir = np.stack([lp(ir[:, 0], 5000), lp(ir[:, 1], 5000)], 1)
    ir /= np.sqrt((ir ** 2).sum(0))
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - wet) + y * wet * 2.2


mixd = reverb(music, 2.4, 0.28) * 0.9 + reverb(sfx, 1.2, 0.15)
mixd = np.stack([hp(mixd[:, c], 28) for c in range(2)], 1)
# мягкий компрессор/лимитер
peak = np.max(np.abs(mixd))
mixd = mixd / peak * 1.25
mixd = np.tanh(mixd) * 0.89
# микро-фейд в самом начале и затухание хвоста к концу
f_in = np.minimum(1, tt(N) / 0.01)
f_out = np.clip((DUR - tt(N)) / 0.9, 0, 1) ** 0.7
mixd *= (f_in * np.minimum(1, f_out + 0.0))[:, None]
os.makedirs(os.path.join(ROOT, 'audio'), exist_ok=True)
out = os.path.join(ROOT, 'audio', 'mix.wav')
wavfile.write(out, SR, (mixd * 2 ** 31 * 0.999).astype(np.int32))
print('written', out, 'peak', np.max(np.abs(mixd)), 'rms dB', 20 * np.log10(np.sqrt(np.mean(mixd ** 2))))
