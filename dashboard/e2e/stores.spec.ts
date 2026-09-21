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

test('widget builder uses vector icons and remains responsive', async ({ page }) => {
  await page.route('**/api/v1/stores/store-1', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      id: 'store-1',
      widget_token: 'widget-token',
      name: 'Example Store',
      platform: 'custom',
      is_active: true,
      sync_frequency_hours: 24,
      widget_config: {
        theme: 'light',
        primary_color: '#863bff',
        position: 'bottom-right',
        border_radius: 'md',
        placeholder_text: 'Search for products...',
        show_price: true,
        enable_autocomplete: true,
      },
      search_config: {
        min_score_threshold: 0.25,
        exclude_out_of_stock: false,
      },
    }),
  }));

  await page.goto('/stores/store-1/settings');

  await expect(page.getByRole('heading', { name: 'Widget Builder' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Light UI' }).locator('svg')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Dark UI' }).locator('svg')).toBeVisible();
  await expect(page.getByText('Merchant Storefront', { exact: true })).toBeVisible();
  await expect(page.getByText('Pro-Run Orthotic Sneakers')).toBeVisible();

  const emojiCount = await page.locator('body').evaluate((body) => {
    const text = body.textContent || '';
    return (text.match(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu) || []).length;
  });
  expect(emojiCount).toBe(0);

  const overflow = await page.evaluate(() => ({
    viewportWidth: window.innerWidth,
    documentWidth: document.documentElement.scrollWidth,
  }));
  expect(overflow.documentWidth).toBeLessThanOrEqual(overflow.viewportWidth + 1);
});
