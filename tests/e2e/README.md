# E2E Tests with Playwright

End-to-end tests for the Assets Manager application.

## Setup

1. Install Playwright browsers:
   ```bash
   npx playwright install chromium
   ```

2. Make sure your application is running with all required Docker containers:
   ```bash
   # Start your Docker containers
   docker-compose up -d
   
   # Start the app with auth disabled for testing
   FLASK_DISABLE_AUTH_FOR_TESTS=true
   dotrun
   ```

## Running Tests

```bash
# Run all e2e tests (headless)
yarn run test-e2e

# Run tests with UI mode (interactive)
yarn run test-e2e-ui

# Run tests in headed mode (see browser)
yarn run test-e2e-headed

# Run specific test file
npx playwright test homepage.spec.js
```

## Configuration

- Test directory: `tests/e2e/`
- Configuration file: `playwright.config.ts`

## Writing Tests

Test files should follow the pattern `*.spec.ts` and be placed in `tests/e2e/`.

Example:
```typescript
import { test, expect } from '@playwright/test';

test('my test', async ({ page }) => {
  await page.goto('/manager');
  await expect(page).toHaveTitle(/Manager/);
});
```
