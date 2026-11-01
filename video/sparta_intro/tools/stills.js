// node tools/stills.js out_dir t1 t2 ...  — кадры для проверки композиции
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
  const ts = process.argv.slice(3).map(Number);
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('console', m => console.log('console:', m.text())); p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto('file://' + path.resolve(__dirname, '../index.html') + '?export=1');
  await p.waitForFunction(() => window.isReady && window.isReady());
  for (const t of ts) {
    const t0 = Date.now(); await p.evaluate(t => renderAt(t), t);
    await p.locator('canvas').screenshot({ path: `${out}/t${t.toFixed(2).padStart(6, '0')}.png` });
    console.log(t, Date.now() - t0, 'ms');
  }
  await b.close();
})();
