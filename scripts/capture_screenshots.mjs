import { chromium } from 'playwright';

async function capture() {
  const browser = await chromium.launch({
    channel: 'msedge',
    headless: true
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    permissions: ['camera', 'microphone']
  });

  const page = await context.newPage();
  console.log('Navigating to live site (domcontentloaded)...');
  await page.goto('https://wayangbali.hikari.my.id', { waitUntil: 'domcontentloaded', timeout: 20000 });
  await page.waitForTimeout(5000);

  // 1. Home Screen
  console.log('Taking screenshot of Home Screen...');
  await page.screenshot({ path: 'screenshot_home.png' });

  // 2. Character Selection Screen
  console.log('Looking for Character Selection button...');
  const selectBtn = page.locator('button[data-action="select"]');
  if (await selectBtn.count() > 0) {
    console.log('Clicking to Character Selection...');
    await selectBtn.first().click();
    await page.waitForTimeout(3000);
    console.log('Taking screenshot of Character Selection...');
    await page.screenshot({ path: 'screenshot_character_selection.png' });
  } else {
    console.log('button[data-action="select"] not found');
  }

  // 3. AI Tutor Screen
  console.log('Looking for AI Tutor button...');
  const tutorBtn = page.locator('button[data-action="tutor"]');
  if (await tutorBtn.count() > 0) {
    console.log('Clicking AI Tutor...');
    await tutorBtn.first().click();
    await page.waitForTimeout(3000);
    console.log('Taking screenshot of AI Tutor Screen...');
    await page.screenshot({ path: 'screenshot_tutor.png' });
  } else {
    console.log('button[data-action="tutor"] not found, returning to home...');
    await page.goto('https://wayangbali.hikari.my.id', { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(3000);
    const tutorHomeBtn = page.locator('button[data-action="tutor"]');
    if (await tutorHomeBtn.count() > 0) {
      await tutorHomeBtn.first().click();
      await page.waitForTimeout(3000);
      console.log('Taking screenshot of AI Tutor Screen...');
      await page.screenshot({ path: 'screenshot_tutor.png' });
    }
  }

  await browser.close();
  console.log('Screenshots process finished!');
}

capture().catch(err => {
  console.error('Error during capture:', err);
  process.exit(1);
});
