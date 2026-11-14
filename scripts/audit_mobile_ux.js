const { chromium } = require('playwright');
const path = require('path');

const ARTIFACTS_DIR = '/Users/aryansharma/.gemini/antigravity/brain/be9c555d-2eed-480c-a588-0af0acb7b799';

async function auditUx() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  });

  try {
    // Mobile iPhone Viewport
    const mobileContext = await browser.newContext({
      viewport: { width: 390, height: 844 },
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    });
    try {
      const page = await mobileContext.newPage();

      console.log('[Audit] Testing Mobile Login Flow...');
      await page.goto('http://127.0.0.1:5050/login');
      await page.waitForTimeout(500);

      // Check form submit
      const pin = process.env.FRONTIER_MASTER_PIN || 'frontier-orbitron-2026';
      await page.fill('#pinInput', pin);
      await page.click('#unlockBtn');
      await page.waitForURL(/5050\/(frontierpilot)?/, { timeout: 10000 });
      await page.waitForTimeout(1000);

      console.log('[Audit] Capturing Mobile Cockpit Screenshot...');
      await page.screenshot({ path: path.join(ARTIFACTS_DIR, 'frontierpilot-ux-mobile-cockpit.png') });

      // Evaluate Mobile Issues
      const mobileMetrics = await page.evaluate(() => {
        const issues = [];
        // Check horizontal scroll / overflow
        if (document.documentElement.scrollWidth > window.innerWidth) {
          issues.push(`Horizontal overflow detected: page width ${document.documentElement.scrollWidth}px > viewport ${window.innerWidth}px`);
        }

        // Check sidebar visibility on mobile
        const sidebar = document.querySelector('.frontierpilot-sidebar');
        if (sidebar) {
          const rect = sidebar.getBoundingClientRect();
          const style = window.getComputedStyle(sidebar);
          if (style.display !== 'none' && rect.width > 200 && window.innerWidth < 600) {
            issues.push(`Desktop sidebar is taking ${rect.width}px on a ${window.innerWidth}px mobile screen without collapsible toggle`);
          }
        }

        // Check touch target sizes
        const buttons = document.querySelectorAll('button, a.btn');
        let smallTargets = 0;
        buttons.forEach(b => {
          const r = b.getBoundingClientRect();
          if (r.width > 0 && r.height > 0 && (r.width < 40 || r.height < 40)) {
            smallTargets++;
          }
        });
        if (smallTargets > 0) {
          issues.push(`${smallTargets} touch targets smaller than recommended 44x44px mobile size`);
        }

        return {
          scrollWidth: document.documentElement.scrollWidth,
          viewportWidth: window.innerWidth,
          issues: issues
        };
      });

      console.log('[Audit] Mobile UX Metrics:', JSON.stringify(mobileMetrics, null, 2));
      return mobileMetrics;
    } finally {
      await mobileContext.close();
    }
  } finally {
    await browser.close();
  }
}

auditUx().catch(err => {
  console.error('[Audit Error]', err);
  process.exit(1);
});
