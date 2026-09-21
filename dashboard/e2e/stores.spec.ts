import { expect, test } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('token', 'test-token'));

  await page.route('**/api/v1/auth/me', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      id: 'user-1',
      email: 'merchant@example.com',
      full_name: 'Merchant',
      is_active: true,
      is_verified: true,
    }),
  }));

  await page.route('**/api/v1/stores/', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{
      id: 'store-1',
      widget_token: 'widget-token',
      name: 'Example Store',
      platform: 'custom',
      is_active: true,
      sync_frequency_hours: 24,
      index_status: 'ready',
      indexed_product_count: 0,
      total_product_count: 0,
    }]),
  }));
});

test('store list tolerates an incomplete analytics response', async ({ page }) => {
  await page.route('**/api/v1/analytics/store-1?days=7', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ total_searches: 0 }),
  }));

  await page.goto('/stores');

  await expect(page.getByRole('heading', { name: 'My Stores' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Example Store' })).toBeVisible();
  await expect(page.getByText('All stores')).toBeVisible();
  await expect(page.getByText("Cannot read properties of undefined")).toHaveCount(0);
  await expect(page.getByText('0', { exact: true }).first()).toBeVisible();
});
