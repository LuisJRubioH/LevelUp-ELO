import { chromium } from 'playwright';
import * as fs from 'node:fs';
const SHOT_DIR = 'C:\\Users\\orian\\AppData\\Local\\Temp\\oulad_shots';
const errors = [];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await ctx.newPage();
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push(msg.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));

  await page.goto('http://localhost:5173/login', { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('input[type="text"]', { timeout: 15000 });
  await page.fill('input[type="text"]', 'estudiante1');
  await page.fill('input[type="password"]', 'demo1234');
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/student/, { timeout: 15000 });

  await page.goto('http://localhost:5173/student/course/calculo_diferencial/map', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);
  await page.screenshot({ path: SHOT_DIR + '\\60-map-with-panel.png', fullPage: true });

  // mobile width too (panel debe ocultarse)
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(400);
  await page.screenshot({ path: SHOT_DIR + '\\61-map-mobile.png', fullPage: true });

  console.log('CONSOLE_ERRORS:', JSON.stringify(errors));
  await browser.close();
})().catch((e) => { console.error('FATAL:', e); process.exit(1); });
