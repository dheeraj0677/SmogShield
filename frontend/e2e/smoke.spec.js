import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

test.describe('SmogShield E2E smoke test', () => {
  test('loads dashboard, passes WCAG 2.1 AA axe scan, switches tabs, and chats', async ({
    page,
  }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'SmogShield', exact: true })).toBeVisible();
    await expect(page.getByRole('meter')).toBeVisible({ timeout: 15000 });
    await expect(page.getByText(/24-Hour Diurnal Smog Cycle/i)).toBeVisible();

    const axeResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
    expect(axeResults.violations).toEqual([]);

    await page.getByRole('tab', { name: 'Indoor Air Hacks' }).click();
    await expect(page.getByText(/Room CADR & Clean-Air Decay Solver/i)).toBeVisible();

    await page.getByRole('tab', { name: 'Clean Commute' }).click();
    await expect(page.getByText(/Dijkstra Clean-Corridor Router/i)).toBeVisible();
    await expect(page.getByText(/Recommended Clean Path/i)).toBeVisible({ timeout: 10000 });

    await page.getByRole('tab', { name: 'Community & Alerts' }).click();
    await page.getByRole('button', { name: /Urdu/i }).click();
    await expect(
      page.getByLabel(/Multilingual emergency smog advisory/i)
    ).toHaveAttribute('dir', 'rtl');

    const chatInput = page.getByLabel(/Ask SmogShield/i);
    await chatInput.fill('What indoor air hack should I prioritize tonight?');
    await page.getByRole('button', { name: 'Send message' }).click();

    await expect(
      page.locator('article[aria-label="SmogShield assistant response"]').nth(1)
    ).toBeVisible({ timeout: 25000 });
  });

  test('renders cleanly on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'SmogShield', exact: true })).toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Open household context settings' })
    ).toBeVisible();
  });
});
