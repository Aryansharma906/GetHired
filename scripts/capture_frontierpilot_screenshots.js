const { chromium } = require('playwright');
const path = require('path');

const ARTIFACTS_DIR = '/Users/aryansharma/.gemini/antigravity/brain/be9c555d-2eed-480c-a588-0af0acb7b799';

async function capture() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1100 }
  });
  const page = await context.newPage();

  console.log('Navigating to login page...');
  await page.goto('http://127.0.0.1:5050/login');
  await page.waitForTimeout(1000);

  console.log('Entering PIN and logging in...');
  const pin = process.env.FRONTIER_MASTER_PIN || 'frontier-orbitron-2026';
  await page.fill('#pinInput', pin);
  await page.click('#unlockBtn');
  await page.waitForURL(/5050\/(frontierpilot)?/, { timeout: 10000 });
  await page.waitForTimeout(2000);

  // 1. Creator Studio Tab
  console.log('Switching to Creator Studio Tab...');
  await page.evaluate(() => switchFrontierPilotTab('creator-studio'));
  await page.waitForTimeout(2000);
  console.log('Capturing Creator Studio...');
  await page.screenshot({ path: path.join(ARTIFACTS_DIR, 'frontierpilot-cosmic-creator-studio.png') });

  // 2. Multi-Sync Hub Tab
  console.log('Switching to Sync Hub Tab...');
  await page.evaluate(() => switchFrontierPilotTab('sync'));
  await page.waitForTimeout(1500);
  console.log('Capturing Sync Hub...');
  await page.screenshot({ path: path.join(ARTIFACTS_DIR, 'frontierpilot-cosmic-sync-hub.png') });

  // 3. AI Stack & Vaibhav Growth Studio Tab
  console.log('Switching to AI Stack & Vaibhav Growth Studio Tab...');
  await page.evaluate(() => switchFrontierPilotTab('ai-stack'));
  await page.waitForTimeout(1500);
  console.log('Capturing Vaibhav Growth Studio...');
  await page.screenshot({ path: path.join(ARTIFACTS_DIR, 'frontierpilot-vaibhav-growth-studio.png') });

  await browser.close();
  console.log('Done capturing screenshots!');
}

capture().catch(err => {
  console.error('Error during capture:', err);
  process.exit(1);
});
