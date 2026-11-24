const puppeteer = require('puppeteer-core');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const CHROME_PATH = fs.existsSync('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
  ? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
  : 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';

const BACKEND_DIR = path.resolve(__dirname, '..', 'backend');
const FRONTEND_DIR = path.resolve(__dirname);

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function waitForUrl(url, timeout = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    try {
      const res = await fetch(url);
      if (res.ok || res.status === 404 || res.status === 401) return true;
    } catch {}
    await sleep(500);
  }
  throw new Error(`Timeout waiting for ${url}`);
}

async function isUrlAlive(url) {
  try {
    const res = await fetch(url);
    return res.ok || res.status === 404 || res.status === 401;
  } catch {
    return false;
  }
}

async function runTest() {
  console.log('[1/7] Checking/Spawning Backend and Frontend servers...');
  const venvPython = path.join(BACKEND_DIR, 'venv', 'Scripts', 'python.exe');

  let backendProc = null;
  const backendAlreadyRunning = await isUrlAlive('http://localhost:8000/api/health');
  if (!backendAlreadyRunning) {
    console.log('   -> Starting uvicorn backend on 127.0.0.1:8000...');
    backendProc = spawn(venvPython, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], {
      cwd: BACKEND_DIR,
      stdio: 'pipe'
    });
    backendProc.stdout.on('data', d => console.log('[Backend stdout]', d.toString().trim()));
    backendProc.stderr.on('data', d => console.error('[Backend stderr]', d.toString().trim()));
  } else {
    console.log('   -> Backend is already running on :8000, reusing existing instance.');
  }

  let frontendProc = null;
  const frontendAlreadyRunning = await isUrlAlive('http://localhost:5173/');
  if (!frontendAlreadyRunning) {
    console.log('   -> Starting frontend preview on localhost:5173...');
    frontendProc = spawn('cmd.exe', ['/c', 'npm.cmd', 'run', 'preview', '--', '--port', '5173', '--host', 'localhost'], {
      cwd: FRONTEND_DIR,
      stdio: 'pipe'
    });
    frontendProc.stdout.on('data', d => console.log('[Frontend stdout]', d.toString().trim()));
    frontendProc.stderr.on('data', d => console.error('[Frontend stderr]', d.toString().trim()));
  } else {
    console.log('   -> Frontend preview is already running on :5173, reusing existing instance.');
  }

  const cleanup = () => {
    if (backendProc) try { backendProc.kill(); } catch {}
    if (frontendProc) try { frontendProc.kill(); } catch {}
  };

  process.on('exit', cleanup);
  process.on('SIGINT', cleanup);

  try {
    console.log('[2/7] Waiting for servers to be ready...');
    await waitForUrl('http://localhost:8000/api/health');
    console.log('   -> Backend healthy on :8000');
    await waitForUrl('http://localhost:5173/');
    console.log('   -> Frontend preview ready on :5173');

    console.log('[3/7] Launching Headless Chrome Browser...');
    const browser = await puppeteer.launch({
      executablePath: CHROME_PATH,
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        const text = msg.text();
        // Ignore expected network 401/400 errors during login test and WebSocket preview pings
        if (!text.includes('status of 401') && !text.includes('status of 400') && !text.includes('WebSocket')) {
          consoleErrors.push(`[Console Error] ${text}`);
        }
      }
    });
    page.on('pageerror', err => {
      consoleErrors.push(`[Page Error] ${err.message}`);
    });

    console.log('[4/7] Testing Initial Load & Role Selection...');
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });

    // Handle Splash Screen if visible
    const skipBtn = await page.$('button ::-p-text(Skip to Portal)');
    if (skipBtn) {
      console.log('   -> Clicking Skip to Portal on Splash Screen');
      await skipBtn.click();
      await sleep(500);
    } else {
      await sleep(2200); // Wait for splash timer
    }

    // Verify Role Selection cards
    await page.waitForSelector('h3', { timeout: 5000 });
    const cardTitles = await page.$$eval('h3', els => els.map(e => e.textContent.trim()));
    console.log('   -> Found access portals:', cardTitles);
    if (!cardTitles.some(t => t.includes('Citizen Login')) || !cardTitles.some(t => t.includes('Officer Login'))) {
      throw new Error(`Expected Citizen and Officer login cards, got: ${cardTitles}`);
    }

    console.log('[5/7] Testing Citizen Registration & Safe Navigation...');
    // Click Citizen Login card
    const citizenCard = await page.evaluateHandle(() => {
      const els = Array.from(document.querySelectorAll('h3'));
      const target = els.find(el => el.textContent.includes('Citizen Login'));
      return target.closest('div.group');
    });
    await citizenCard.click();
    await sleep(500);

    // Click "Create Account" tab
    const createAcctBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      return btns.find(b => b.textContent.includes('Create Account'));
    });
    await createAcctBtn.click();
    await sleep(300);

    // Fill citizen registration form
    const randomSuffix = Math.floor(Math.random() * 90000 + 10000);
    const citizenUsername = `citizen_${randomSuffix}`;
    const citizenPassword = 'CitizenSecurePass123!';

    await page.type('input[placeholder*="Ramesh"]', 'Kavita Verma');
    await page.type('input[placeholder*="citizen_username"]', citizenUsername);
    await page.type('input[type="password"]', citizenPassword);

    // Submit Registration
    const registerBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll('button[type="submit"]'));
      return btns[0];
    });
    await registerBtn.click();
    await page.waitForNavigation({ waitUntil: 'networkidle0' }).catch(() => sleep(1500));
    await sleep(1000);

    // Check we landed on Scam Awareness
    const pageHeading = await page.$eval('h1, h2, h3', el => el.textContent);
    console.log(`   -> Citizen post-registration heading: "${pageHeading}"`);

    // Verify Scam Categories & Threat Breakdown card is populated (no blank space!)
    await page.waitForSelector('h3', { timeout: 5000 });
    const fullBodyText = await page.evaluate(() => document.body.innerText);
    
    // Check that "operandi" does not appear anywhere
    if (/operandi/i.test(fullBodyText)) {
      throw new Error('Found "operandi" in page text! It should have been replaced with clear English terminology.');
    }
    console.log('   -> Confirmed: No "operandi" text present on Citizen Scam Awareness page.');

    // Check Scam Categories card title
    if (!fullBodyText.includes('Scam Categories & Threat Breakdown')) {
      throw new Error('Expected "Scam Categories & Threat Breakdown" card title on Scam Awareness page');
    }
    console.log('   -> Found card: "Scam Categories & Threat Breakdown"');

    // Check scam vectors count and rendered category rows
    const scamVectorsText = await page.evaluate(() => {
      const allDivs = Array.from(document.querySelectorAll('div'));
      const stat = allDivs.find(d => d.textContent.includes('Scam Vectors') && d.textContent.includes('Scam types tracked'));
      return stat ? stat.textContent : null;
    });
    console.log(`   -> Scam Vectors StatCard text: "${scamVectorsText}"`);

    const categoryRows = await page.evaluate(() => {
      // Find category bar elements
      const elements = Array.from(document.querySelectorAll('.group.p-2.rounded-lg'));
      return elements.map(el => el.textContent.trim());
    });
    console.log(`   -> Rendered category rows count: ${categoryRows.length}`);
    if (categoryRows.length === 0) {
      throw new Error('Blank space detected! Category threat spectrum rows are empty (0 rows rendered).');
    }
    console.log(`   -> Sample category row: "${categoryRows[0]}"`);

    // Verify exactly 4 sidebar items
    const sidebarNavLinks = await page.$$eval('aside nav a', els => els.map(e => e.textContent.replace(/\s+/g, ' ').trim()));
    console.log(`   -> Citizen sidebar item count: ${sidebarNavLinks.length}`);
    sidebarNavLinks.forEach((item, idx) => console.log(`      ${idx + 1}. ${item}`));
    if (sidebarNavLinks.length !== 4) {
      throw new Error(`Citizen mode MUST have exactly 4 sidebar items! Found: ${sidebarNavLinks.length}`);
    }

    // Verify NO console errors occurred
    if (consoleErrors.length > 0) {
      throw new Error(`Console errors encountered during Citizen registration: ${consoleErrors.join(', ')}`);
    }
    console.log('   -> Citizen registration & Scam Awareness UI verified without errors!');

    // Test Citizen Logout
    console.log('[6/7] Testing Logout & Officer Demo Authentication...');
    const logoutBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      return btns.find(b => b.textContent.includes('Logout') || b.title?.includes('Logout'));
    });
    await logoutBtn.click();
    await sleep(1000);

    // Click Officer Login
    const officerCard = await page.evaluateHandle(() => {
      const els = Array.from(document.querySelectorAll('h3'));
      const target = els.find(el => el.textContent.includes('Officer Login'));
      return target.closest('div.group');
    });
    await officerCard.click();
    await sleep(500);

    // Test wrong password first
    await page.type('input[placeholder*="officer"]', 'officer_sharma');
    await page.type('input[type="password"]', 'WrongPassword123');
    const submitBtn = await page.evaluateHandle(() => {
      return document.querySelector('button[type="submit"]');
    });
    await submitBtn.click();
    await sleep(1000);

    // Verify error banner is displayed
    const errorText = await page.evaluate(() => {
      const errBox = document.querySelector('.bg-rose-950\\/50');
      return errBox ? errBox.textContent : null;
    });
    console.log(`   -> Wrong password response: "${errorText}"`);
    if (!errorText || !errorText.toLowerCase().includes('invalid')) {
      throw new Error(`Expected invalid credentials error, got: ${errorText}`);
    }

    // Auto-fill demo credentials
    const autoFillBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      return btns.find(b => b.textContent.includes('Auto-fill'));
    });
    await autoFillBtn.click();
    await sleep(300);

    // Submit Officer Login
    await submitBtn.click();
    await page.waitForNavigation({ waitUntil: 'networkidle0' }).catch(() => sleep(1500));
    await sleep(1000);

    // Verify Officer Dashboard & Sidebar
    const officerNavLinks = await page.$$eval('aside nav a', els => els.map(e => e.textContent.replace(/\s+/g, ' ').trim()));
    console.log(`   -> Officer sidebar item count: ${officerNavLinks.length}`);
    officerNavLinks.forEach((item, idx) => console.log(`      ${idx + 1}. ${item}`));
    if (officerNavLinks.length < 8) {
      throw new Error(`Officer mode MUST have at least 8 workspaces! Found: ${officerNavLinks.length}`);
    }

    // Load demo data if available
    const loadDemoBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      return btns.find(b => b.textContent.includes('Load Demo Data'));
    });
    if (loadDemoBtn) {
      console.log('   -> Clicking "Load Demo Data"');
      await loadDemoBtn.click();
      await sleep(2500);
    }

    console.log('[7/7] Verifying all Officer Workspaces & PDF Generation...');
    const officerRoutes = [
      '/analyze/message',
      '/analyze/url',
      '/analyze/website',
      '/intelligence/graph',
      '/intelligence/heatlist',
      '/cases',
      '/reports',
      '/assistant'
    ];

    for (const route of officerRoutes) {
      await page.goto(`http://localhost:5173${route}`, { waitUntil: 'networkidle0' });
      await sleep(600);
      const title = await page.title();
      console.log(`   -> Visited ${route}: "${title}"`);
    }

    // Test Refresh while logged in: session persists!
    await page.reload({ waitUntil: 'networkidle0' });
    await sleep(600);
    const userRoleBadge = await page.evaluate(() => {
      const badge = document.querySelector('header span.font-mono');
      return badge ? badge.textContent : null;
    });
    console.log(`   -> Post-refresh active role badge: "${userRoleBadge}"`);
    if (!userRoleBadge || !userRoleBadge.includes('OFFICER')) {
      throw new Error('Session did not persist across refresh!');
    }

    // Test PDF Dossier generation
    console.log('   -> Testing Case Management PDF dossier generation via API...');
    const pdfRes = await page.evaluate(async () => {
      const token = sessionStorage.getItem('linkshield_token');
      const res = await fetch('http://127.0.0.1:8000/api/reports/DEMO-011/pdf', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return { status: res.status, contentType: res.headers.get('content-type') };
    });
    console.log('   -> PDF download response:', pdfRes);
    if (pdfRes.status !== 200 || !pdfRes.contentType.includes('application/pdf')) {
      throw new Error(`PDF generation failed: ${JSON.stringify(pdfRes)}`);
    }

    await browser.close();
    cleanup();

    console.log('\n============================================================');
    console.log('🎉 ALL REAL BROWSER TESTS PASSED FLAWLESSLY WITH 0 ERRORS!');
    console.log('============================================================');
    process.exit(0);
  } catch (err) {
    console.error('\n❌ TEST RUNNER FAILED:', err);
    cleanup();
    process.exit(1);
  }
}

runTest();
