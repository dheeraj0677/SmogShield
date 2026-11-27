import { expect, test } from '@playwright/test';

test.describe('SmogShield E2E smoke test', () => {
  test('loads dashboard, CADR solver, Dijkstra transit, community RTL, and chat', async ({
    page,
  }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'SmogShield', exact: true })).toBeVisible();
    await expect(page.getByRole('meter')).toBeVisible({ timeout: 15000 });
    await expect(page.getByText(/24-Hour Diurnal Smog Cycle/i)).toBeVisible();

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
      page.getByText(/Tailored Action Plan|Current Air Quality Snapshot/i).first()
    ).toBeVisible({ timeout: 15000 });
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
