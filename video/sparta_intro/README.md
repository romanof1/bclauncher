# Спарта — вступление (motion-ролик)

Готовый файл: `sparta_intro.mp4`. Параметры: 1920×1080, 60 fps, H.264 yuv420p, AAC 48 кГц стерео, 41,4 с.

| Файл | Что это |
|---|---|
| `STORYBOARD.md` | идея, варианты по сценам, выбранная раскадровка |
| `index.html` | весь ролик: детерминированный таймлайн `renderAt(t)` на Canvas. Превью открывается в браузере, есть кнопка ▶ и скраббер |
| `fonts/` | Oswald и Playfair Display (OFL), кириллица |
| `audio/mix.wav` | музыка и SFX (синтез), `audio/events.json` — точки синхронизации из анимации |
| `tools/` | скрипты рендера и сведения |

## Пересборка

```bash
node tools/events.js > audio/events.json
```

```bash
python3 tools/synth.py
```

```bash
node tools/render.js /tmp/sparta_render 4
```

```bash
tools/mux.sh /tmp/sparta_render sparta_intro.mp4
```

Тексты и тайминги лежат в массивах `textsA…textsD` в `index.html`, у каждой фразы есть время входа `t0` и выхода `t1`. Чтобы подогнать ролик под ваш дикторский темп, достаточно сдвинуть эти значения и пересобрать.
