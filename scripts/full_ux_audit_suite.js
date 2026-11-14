const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const ARTIFACTS_DIR = '/Users/aryansharma/.gemini/antigravity/brain/be9c555d-2eed-480c-a588-0af0acb7b799';
const BASE_URL = 'http://127.0.0.1:5050';
const PIN = process.env.FRONTIER_MASTER_PIN || 'frontier-orbitron-2026';

const VIEWPORTS = [
  { name: 'desktop-1440', width: 1440, height: 900, isMobile: false },
  { name: 'laptop-1280', width: 1280, height: 800, isMobile: false },
  { name: 'tablet-landscape-1024', width: 1024, height: 768, isMobile: false },
  { name: 'tablet-portrait-768', width: 768, height: 1024, isMobile: true },
  { name: 'mobile-iphone-390', width: 390, height: 844, isMobile: true },
  { name: 'mobile-se-375', width: 375, height: 667, isMobile: true },
  { name: 'mobile-narrow-320', width: 320, height: 568, isMobile: true },
];

const TABS = [
  { slug: 'dashboard', id: 'tabDashboard', name: 'Executive Dashboard' },
  { slug: 'kanban', id: 'tabKanban', name: 'Kanban Pipeline' },
  { slug: 'roles', id: 'tabRoles', name: 'Target Roles & Radar' },
  { slug: 'resumes', id: 'tabResumes', name: 'Tailored Dossiers' },
  { slug: 'profile', id: 'tabProfile', name: 'Master Profile' },
  { slug: 'ai-stack', id: 'tabAiStack', name: 'AI Stack & Vaibhav Growth Studio' },
  { slug: 'outreach', id: 'tabOutreach', name: 'Founder Outreach' },
  { slug: 'learning', id: 'tabLearning', name: 'Skill Matrix & Learning' },
  { slug: 'creator-studio', id: 'tabCreatorStudio', name: 'LinkedIn Creator Studio' },
  { slug: 'sync', id: 'tabSync', name: 'Multi-Cloud Sync Hub' },
];

async function runComprehensiveAudit() {
  console.log('🚀 Launching Full FrontierPilot 2.0 UI/UX Quality Stress-Test...');

  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  });

  const auditReport = {
    timestamp: new Date().toISOString(),
    viewports: {},
    accessibility: {},
    tabInteractions: {},
    modals: {},
    summaryScores: {}
  };

  try {
    // 1. Initial Authentication & Responsive Viewport Matrix
    for (const vp of VIEWPORTS) {
      console.log(`\n📱 Auditing Viewport: ${vp.name} (${vp.width}x${vp.height})...`);
      const context = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        isMobile: vp.isMobile,
        hasTouch: vp.isMobile
      });

      const page = await context.newPage();

      // Login
      await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(300);
      await page.fill('#pinInput', PIN);
      await page.click('#unlockBtn');
      await page.waitForURL(/5050\/(frontierpilot)?/, { timeout: 10000 });
      await page.waitForTimeout(800);

      // Evaluate Horizontal Overflow & DOM Metrics
      const vpMetrics = await page.evaluate((vpWidth) => {
        const issues = [];
        const docWidth = document.documentElement.scrollWidth;
        const bodyWidth = document.body.scrollWidth;
        const winWidth = window.innerWidth;

        if (docWidth > winWidth + 2) {
          issues.push({
            type: 'HORIZONTAL_OVERFLOW',
            detail: `Document scrollWidth (${docWidth}px) exceeds window.innerWidth (${winWidth}px) by ${docWidth - winWidth}px`
          });
        }

        // Check touch target sizes (< 44x44px per WCAG 2.5.5 / 2.5.8)
        let sub44Targets = 0;
        let sub32Targets = 0;
        const interactiveElements = document.querySelectorAll('button, a.btn, input, select, textarea, .nav-link');
        interactiveElements.forEach(el => {
          const rect = el.getBoundingClientRect();
          if (rect.width > 0 && rect.height > 0) {
            if (rect.width < 44 || rect.height < 44) sub44Targets++;
            if (rect.width < 32 || rect.height < 32) sub32Targets++;
          }
        });

        // Check sidebar behavior
        const sidebar = document.querySelector('.frontierpilot-sidebar');
        let sidebarIssue = null;
        if (sidebar) {
          const rect = sidebar.getBoundingClientRect();
          const style = window.getComputedStyle(sidebar);
          if (vpWidth < 768 && style.display !== 'none' && rect.width > 200) {
            sidebarIssue = `Sidebar occupies ${rect.width}px on mobile without collapsible overlay`;
          }
        }

        return {
          scrollWidth: docWidth,
          innerWidth: winWidth,
          sub44Targets,
          sub32Targets,
          sidebarIssue,
          issues
        };
      }, vp.width);

      // Capture screenshot at this viewport
      const screenshotPath = path.join(ARTIFACTS_DIR, `audit-${vp.name}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: false });

      auditReport.viewports[vp.name] = {
        metrics: vpMetrics,
        screenshot: screenshotPath
      };

      console.log(`   • Overflow: ${vpMetrics.issues.length ? '⚠️ DETECTED' : '✅ NONE'}`);
      console.log(`   • Small Touch Targets (<44px): ${vpMetrics.sub44Targets}`);

      await context.close();
    }

    // 2. Comprehensive Tab-by-Tab Navigation & Interactive Functional Audit (at 1440px Desktop)
    console.log('\n🖥️ Auditing Tab Navigation, State Management & Modals at 1440px...');
    const desktopContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const deskPage = await desktopContext.newPage();

    await deskPage.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
    await deskPage.fill('#pinInput', PIN);
    await deskPage.click('#unlockBtn');
    await deskPage.waitForURL(/5050\/(frontierpilot)?/, { timeout: 10000 });
    await deskPage.waitForTimeout(600);

    for (const tab of TABS) {
      console.log(`   Testing Tab: ${tab.name} (${tab.slug} -> #${tab.id})...`);
      const navBtnSelector = `button[onclick*="'${tab.slug}'"]`;
      const tabExists = await deskPage.$(navBtnSelector);

      if (tabExists) {
        await deskPage.click(navBtnSelector);
        await deskPage.waitForTimeout(400);

        // Check tab visibility
        const isVisible = await deskPage.evaluate((tabId) => {
          const el = document.getElementById(tabId);
          if (!el) return false;
          const style = window.getComputedStyle(el);
          return style.display !== 'none' && !el.classList.contains('d-none');
        }, tab.id);

        // Check if any errors rendered
        const errorText = await deskPage.evaluate(() => {
          const errAlerts = document.querySelectorAll('.alert-danger:not(.d-none)');
          return Array.from(errAlerts).map(a => a.textContent.trim());
        });

        // Screenshot for tab
        const tabScreenshot = path.join(ARTIFACTS_DIR, `audit-tab-${tab.id}.png`);
        await deskPage.screenshot({ path: tabScreenshot, fullPage: false });

        auditReport.tabInteractions[tab.id] = {
          name: tab.name,
          navigatedSuccessfully: isVisible,
          visibleErrors: errorText,
          screenshot: tabScreenshot
        };
      } else {
        auditReport.tabInteractions[tab.id] = {
          name: tab.name,
          navigatedSuccessfully: false,
          error: `Navigation button ${navBtnSelector} not found in DOM`
        };
      }
    }

    // 3. Modal Lifecycle & Backdrop Cleanup Test
    console.log('\n🔍 Testing Modal Lifecycle, Viewport Locking & Backdrop Disposal...');
    const modalTestResult = await deskPage.evaluate(async () => {
      const results = {};
      const newPostBtn = document.querySelector('button[data-bs-target="#newPostModal"]');
      if (newPostBtn) {
        newPostBtn.click();
        await new Promise(r => setTimeout(r, 400));
        
        const modal = document.getElementById('newPostModal');
        const hasShow = modal ? modal.classList.contains('show') : false;
        const bodyHasModalOpen = document.body.classList.contains('modal-open');
        const backdrop = document.querySelector('.modal-backdrop');

        // Close modal
        const closeBtn = modal ? modal.querySelector('button[data-bs-dismiss="modal"], .btn-close') : null;
        if (closeBtn) closeBtn.click();
        await new Promise(r => setTimeout(r, 400));

        const backdropRemaining = document.querySelector('.modal-backdrop');
        const bodyStillLocked = document.body.classList.contains('modal-open');

        return {
          modalOpened: hasShow,
          bodyModalOpenApplied: bodyHasModalOpen,
          backdropRendered: !!backdrop,
          backdropCleanedUp: !backdropRemaining,
          bodyLockCleanedUp: !bodyStillLocked
        };
      }
      return { status: 'skipped_no_btn' };
    });

    auditReport.modals = modalTestResult;
    console.log('   • Modal Test:', JSON.stringify(modalTestResult));

    // 4. Accessibility (WCAG 2.2 AA) Audit
    console.log('\n♿ Evaluating WCAG 2.2 AA Compliance...');
    const a11yMetrics = await deskPage.evaluate(() => {
      const issues = [];

      // 1. Image alt tags
      const images = document.querySelectorAll('img');
      let missingAlt = 0;
      images.forEach(img => {
        if (!img.hasAttribute('alt')) missingAlt++;
      });
      if (missingAlt > 0) issues.push(`${missingAlt} images missing alt text`);

      // 2. Form control labels
      const inputs = document.querySelectorAll('input, select, textarea');
      let unlabeledInputs = 0;
      inputs.forEach(inp => {
        const id = inp.getAttribute('id');
        const hasAria = inp.hasAttribute('aria-label') || inp.hasAttribute('aria-labelledby');
        const hasLabel = id ? !!document.querySelector(`label[for="${id}"]`) : false;
        if (!hasAria && !hasLabel && inp.type !== 'hidden') unlabeledInputs++;
      });
      if (unlabeledInputs > 0) issues.push(`${unlabeledInputs} form controls lack accessible labels`);

      // 3. Color contrast estimation on prominent headings & text
      const textElements = document.querySelectorAll('.text-muted, .text-secondary, small');
      let lowContrastCount = 0;
      textElements.forEach(el => {
        const style = window.getComputedStyle(el);
        const color = style.color;
        // Check for common low-contrast hex values on dark bg
        if (color === 'rgb(108, 117, 125)' || color === 'rgba(255, 255, 255, 0.4)') {
          lowContrastCount++;
        }
      });
      if (lowContrastCount > 0) issues.push(`${lowContrastCount} secondary text elements have low contrast on dark backgrounds`);

      // 4. Visible focus styles
      const interactive = document.querySelectorAll('button, a.btn');
      let customFocusCount = 0;
      interactive.forEach(btn => {
        const style = window.getComputedStyle(btn);
        if (style.outlineStyle !== 'none' || style.boxShadow.includes('rgba')) {
          customFocusCount++;
        }
      });

      return {
        issues,
        missingAlt,
        unlabeledInputs,
        lowContrastCount,
        focusStyleCoverage: `${Math.round((customFocusCount / Math.max(1, interactive.length)) * 100)}%`
      };
    });

    auditReport.accessibility = a11yMetrics;
    console.log('   • A11y Issues Detected:', a11yMetrics.issues);

    await desktopContext.close();
  } finally {
    await browser.close();
  }

  // Write audit report to artifacts
  const reportPath = path.join(ARTIFACTS_DIR, 'comprehensive_ux_audit_report.json');
  fs.writeFileSync(reportPath, JSON.stringify(auditReport, null, 2));
  console.log(`\n✅ Audit complete! Saved full report to ${reportPath}`);
  return auditReport;
}

runComprehensiveAudit().catch(err => {
  console.error('Fatal audit failure:', err);
  process.exit(1);
});
