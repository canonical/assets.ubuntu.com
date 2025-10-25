import { test, expect } from '@playwright/test';

test.describe('Homepage - Manager Page', () => {
  test('should load the manager homepage', async ({ page }) => {
    await page.goto('/manager');

    // Should stay on manager page (not redirect to login)
    await expect(page).toHaveURL(/.*\/manager/);

    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('should have visible content', async ({ page }) => {
    await page.goto('/manager');
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });

  test('should display main navigation header', async ({ page }) => {
    await page.goto('/manager');

    const banner = page.locator('.p-navigation__banner');
    await expect(banner).toBeVisible();
    await expect(banner).toContainText('Canonical asset manager');
  });
});
