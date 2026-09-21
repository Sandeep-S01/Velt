import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page } from '@playwright/test';

const apiBase = 'http://127.0.0.1:4173/api/v1';

async function mountWidget(page: Page) {
  await page.route('**/api/v1/widget/config/store-e2e', async (route) => {
    expect(route.request().headers()['x-widget-token']).toBe('widget-token-e2e');
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        theme: 'light',
        primary_color: '#4F46E5',
        position: 'bottom-right',
        border_radius: 'md',
        placeholder_text: 'Find a product',
        show_price: true,
        enable_autocomplete: true,
      }),
    });
  });

  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await page.evaluate(() => {
    document.body.innerHTML = '<main><h1>Merchant test storefront</h1></main>';
  });
  await page.addScriptTag({ url: '/widget.js' });
  await page.evaluate(({ base }) => {
    const Widget = (window as typeof window & {
      SmartSearchWidget: new (storeId: string, apiUrl: string, token: string) => unknown;
    }).SmartSearchWidget;
    new Widget('store-e2e', base, 'widget-token-e2e');
  }, { base: apiBase });
  await expect(page.getByRole('button', { name: 'Open product search' })).toBeVisible();
}

test('widget dialog supports keyboard and accessible mobile layout', async ({ page }) => {
  await mountWidget(page);

  const trigger = page.getByRole('button', { name: 'Open product search' });
  await trigger.click();
  const dialog = page.locator('#ss-search-overlay');
  const input = page.getByRole('searchbox', { name: 'Search products' });

  await expect(dialog).toHaveAttribute('aria-hidden', 'false');
  await expect(dialog).toHaveAttribute('role', 'dialog');
  await expect(dialog).toHaveAttribute('aria-label', 'Product search');
  await expect(trigger).toHaveAttribute('aria-expanded', 'true');
  await expect(input).toBeFocused();

  await page.keyboard.press('Shift+Tab');
  await expect(page.getByRole('button', { name: 'Close product search' })).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(input).toBeFocused();

  const overflow = await page.evaluate(() => ({
    viewportWidth: window.innerWidth,
    documentWidth: document.documentElement.scrollWidth,
  }));
  expect(overflow.documentWidth).toBeLessThanOrEqual(overflow.viewportWidth + 1);

  const scan = await new AxeBuilder({ page })
    .include('#ss-search-overlay')
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();
  expect(scan.violations.filter(({ impact }) => impact === 'serious' || impact === 'critical')).toEqual([]);

  await page.keyboard.press('Escape');
  await expect(dialog).toHaveAttribute('aria-hidden', 'true');
  await expect(trigger).toHaveAttribute('aria-expanded', 'false');
  await expect(trigger).toBeFocused();
});

test('widget escapes catalog data and attributes result clicks', async ({ page }) => {
  let searchBody: unknown;
  let clickBody: unknown;

  await page.route('**/api/v1/widget/autocomplete?**', async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({ suggestions: ['gold wedding ring'] }),
    });
  });
  await page.route('**/api/v1/widget/search', async (route) => {
    expect(route.request().headers()['x-widget-token']).toBe('widget-token-e2e');
    searchBody = route.request().postDataJSON();
    await route.fulfill({
      contentType: 'application/json',
      headers: { 'X-Query-Event-Token': 'query-event-e2e' },
      body: JSON.stringify([{
        id: 'hostile-product',
        title: '<img src=x onerror="window.__widgetInjected=true">',
        description: '<script>window.__widgetInjected=true</script>Safe description',
        price: 79.5,
        score: 0.94,
        product_url: 'javascript:window.__widgetInjected=true',
        image_url: 'javascript:window.__widgetInjected=true',
      }]),
    });
  });
  await page.route('**/api/v1/analytics/click', async (route) => {
    clickBody = route.request().postDataJSON();
    await route.fulfill({ contentType: 'application/json', body: '{}' });
  });

  await mountWidget(page);
  await page.getByRole('button', { name: 'Open product search' }).click();
  await page.getByRole('searchbox', { name: 'Search products' }).fill('gold wed');
  await page.getByRole('button', { name: /gold wedding ring/i }).click();

  const result = page.locator('.ss-card');
  await expect(result).toBeVisible();
  await expect(result.locator('.ss-card-title')).toHaveText('<img src=x onerror="window.__widgetInjected=true">');
  await expect(result).toHaveAttribute('href', '#');
  await expect(result.locator('.ss-card-fallback-img')).toBeVisible();
  await expect(result.locator('script')).toHaveCount(0);
  expect(await page.evaluate(() => Boolean((window as typeof window & { __widgetInjected?: boolean }).__widgetInjected))).toBe(false);
  expect(searchBody).toEqual({ store_id: 'store-e2e', query: 'gold wedding ring', limit: 5 });

  const clickRequest = page.waitForRequest('**/api/v1/analytics/click');
  await result.click();
  await clickRequest;
  expect(clickBody).toEqual({
    query_event_token: 'query-event-e2e',
    clicked_product_id: 'hostile-product',
  });
});
