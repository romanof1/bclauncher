// node tools/render.js out_dir workers  — детерминированный покадровый рендер (t = i/60) в сегменты H.264
const { chromium } = require('playwright'); const path = require('path'); const { spawn } = require('child_process'); const fs = require('fs');
const FPS = 60, DUR = +(process.argv[4] || 43.2), NF = Math.round(DUR * FPS);
const out = process.argv[2], WK = +(process.argv[3] || 4); fs.mkdirSync(out, { recursive: true });
async function worker(k) {
  const a = Math.floor(NF * k / WK), b = Math.floor(NF * (k + 1) / WK);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', String(FPS), path.join(out, `seg${k}.mp4`)], { stdio: ['pipe', 'inherit', 'inherit'] });
  const br = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await br.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto('file://' + path.resolve(__dirname, '../index.html') + '?export=1');
  await p.waitForFunction(() => window.isReady && window.isReady());
  const cvs = p.locator('canvas');
  for (let i = a; i < b; i++) {
    await p.evaluate(t => renderAt(t), i / FPS);
    const buf = await cvs.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((i - a) % 60 === 0) console.log(`w${k} ${i - a}/${b - a}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await br.close();
  fs.writeFileSync(path.join(out, `seg${k}.txt`), `${a} ${b}\n`);
}
(async () => { const t0 = Date.now(); await Promise.all([...Array(WK).keys()].map(worker)); console.log('done', (Date.now() - t0) / 1000, 's', NF, 'frames'); })();
