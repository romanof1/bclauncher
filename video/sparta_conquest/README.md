# Спарта: завоевание и три сословия (motion-ролик)

Готовый файл: `sparta_conquest.mp4`. Параметры: 1920×1080, 60 fps, H.264 yuv420p, AAC 48 кГц, 43,2 с.

- `STORYBOARD.md`: раскадровка и карта «референс → что взято».
- `index.html`: весь ролик, детерминированный таймлайн `renderAt(t)`. Превью открывается в браузере.
- `geo.js`: береговые линии Natural Earth 1:10m (Меркатор), Пелопоннес вырезан по Истму.
- `audio/mix.wav`: музыка и SFX в дорийском ладу на ре.
- Тексты и тайминги лежат в массивах `textsH`, `textsM`, `textsV`, у каждой фразы есть время входа `t0` и выхода `t1`.

## Пересборка

```bash
node tools/events.js > audio/events.json
```

```bash
python3 tools/synth.py
```

```bash
node tools/render.js /tmp/conquest_render 4 43.2
```

```bash
tools/mux.sh /tmp/conquest_render sparta_conquest.mp4
```
