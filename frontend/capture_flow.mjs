import puppeteer from 'puppeteer-core';
import path from 'path';

async function run() {
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    args: ['--no-sandbox', '--disable-gpu', '--window-size=1280,850'],
    headless: true,
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 850 });

  console.log('Navigating to http://127.0.0.1:5173...');
  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle0' });

  const artifactDir = '/home/titan/.gemini/antigravity-ide/brain/d307b00a-dff5-43d3-8eb0-778eebf39aa1';
  const testImagePath = '/home/titan/project/visual-ip-checker/backend/data/reference_images/batik_parang_01.jpg';

  console.log('Uploading test image:', testImagePath);
  const fileInput = await page.$('input[type="file"]');
  await fileInput.uploadFile(testImagePath);

  await new Promise((r) => setTimeout(r, 600));
  await page.screenshot({ path: path.join(artifactDir, 'frontend_preview.png') });
  console.log('Saved frontend_preview.png');

  console.log('Clicking Cek Sekarang button...');
  const submitBtn = await page.$('.btn-submit');
  await submitBtn.click();

  console.log('Waiting for results...');
  await page.waitForSelector('.result-summary-box', { timeout: 15000 });

  // Wait for score count-up animation
  await new Promise((r) => setTimeout(r, 1200));

  await page.screenshot({ path: path.join(artifactDir, 'frontend_result_full.png'), fullPage: true });
  console.log('Saved frontend_result_full.png');

  await browser.close();
  console.log('Flow completed successfully.');
}

run().catch((err) => {
  console.error('Flow failed:', err);
  process.exit(1);
});
