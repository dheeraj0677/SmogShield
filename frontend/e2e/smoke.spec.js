import { expect, test } from '@playwright/test';

test.describe('SmogShield E2E smoke test', () => {
  test('loads dashboard, switches plan tabs, and chats with assistant', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'SmogShield' })).toBeVisible();
    await expect(page.getByRole('meter')).toBeVisible({ timeout: 15000 });

    await page.getByRole('tab', { name: 'Indoor Air Hacks' }).click();
    await expect(page.getByText(/Direct Impact:/i).first()).toBeVisible();

    await page.getByRole('tab', { name: 'Sustainable Alternatives' }).click();
    await expect(page.getByText(/CO₂/i).first()).toBeVisible();

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

    await expect(page.getByRole('heading', { name: 'SmogShield' })).toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Open household context settings' })
    ).toBeVisible();
  });
});
