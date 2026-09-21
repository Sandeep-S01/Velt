# Velt Dashboard

React and TypeScript dashboard for merchant onboarding, catalog management, widget configuration, analytics, and Velt's public beta pages.

## Local development

```bash
npm install
npm run dev
```

Configure `VITE_API_URL` and `VITE_WIDGET_URL` from `.env.example` when the API and widget are not served from their production-relative paths.

## Validation

```bash
npm run lint
npm run build
npm audit --audit-level=high
npx playwright install chromium
npm run test:e2e
```

The Playwright suite serves the production build and checks public routes and the distributed widget in desktop and mobile Chromium. It covers serious WCAG A/AA violations, horizontal overflow, widget keyboard focus, hostile catalog rendering, and click attribution.
