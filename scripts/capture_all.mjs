import { chromium } from 'playwright';

async function run() {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  
  console.log('Navigating to https://wayangbali.hikari.my.id ...');
  await page.goto('https://wayangbali.hikari.my.id');
  
  console.log('Waiting for download screen to complete...');
  await page.waitForSelector('#download-screen.is-hidden', { timeout: 35000 });
  await page.waitForTimeout(1500);

  console.log('Capturing Home screen...');
  await page.screenshot({ path: 'screenshot_home.png' });

  console.log('Navigating to Character Selection...');
  const selectBtn = page.locator('button[data-action="select"]');
  if (await selectBtn.count() > 0) {
    await selectBtn.first().click();
    await page.waitForTimeout(2000);
    console.log('Capturing Character Selection screen...');
    await page.screenshot({ path: 'screenshot_character_selection.png' });

    // Back to home
    const backBtn = page.locator('button[data-action="home"]');
    if (await backBtn.count() > 0) {
      await backBtn.first().click();
      await page.waitForTimeout(1500);
    }
  }

  console.log('Navigating to AI Tutor...');
  const tutorBtn = page.locator('button[data-action="tutor"]');
  if (await tutorBtn.count() > 0) {
    await tutorBtn.first().click();
    await page.waitForTimeout(2000);
    console.log('Capturing AI Tutor screen...');
    await page.screenshot({ path: 'screenshot_tutor.png' });
  }

  await browser.close();
  console.log('Done! All screenshots captured.');
}

run().catch(e => {
  console.error('Capture error:', e);
  process.exit(1);
});

