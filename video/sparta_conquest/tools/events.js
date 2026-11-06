const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.resolve(__dirname, '../index.html') + '?export=1');
  await p.waitForFunction(() => window.isReady && window.isReady());
  console.log(JSON.stringify(await p.evaluate(() => soundEvents()))); await b.close(); })();
