import { test, expect } from './fixtures/create-test-assets.fixture';
import { Page } from '@playwright/test';

// So that all the tests run in a single worker and fixtures are only run once
test.describe.configure({ mode: "serial" });


// Helper functions
async function navigateToSearchPage(page: Page) {
  await page.goto('/manager');
  await expect(page.locator('h1.p-muted-heading')).toContainText(
    'Search and filter'
  );
}

async function searchByText(page: Page, searchText: string) {
  const searchInput = page.locator('input#tag');
  await searchInput.fill(searchText);
}

async function selectAssetType(page: Page, assetType: string) {
  await page.locator('select[name="asset_type"]').selectOption(assetType);
}

async function selectCategory(page: Page, category: string) {
  await page.locator('select#category-select').selectOption(category);
}

async function submitSearch(page: Page) {
  await page.getByRole('button', { name: 'Search' }).click();
  await page.waitForLoadState('networkidle');
}

async function getSearchResultsCount(page: Page): Promise<number> {
  const countText = await page.locator('#assets_count').textContent();
  if (!countText) return 0;
  const match = countText.match(/(\d+)\s+asset/);
  return match ? parseInt(match[1], 10) : 0;
}

async function verifySearchResults(page: Page, shouldHaveResults: boolean) {
  if (shouldHaveResults) {
    await expect(
      page.locator('h3.p-heading--5').filter({ hasText: 'Search results' })
    ).toBeVisible();
  } else {
    await expect(
      page
        .locator('h3.p-heading--5')
        .filter({ hasText: 'No results. Please try another search.' })
    ).toBeVisible();
  }
}

test.describe('Asset search and filter', () => {
  // Use the testAssets fixture to ensure test data exists
  test('all search fields are visible', async ({ page, testAssets }) => {
    await navigateToSearchPage(page);

    // Verify all search elements are present
    await expect(page.locator('input#tag')).toBeVisible();
    await expect(page.locator('select[name="asset_type"]')).toBeVisible();
    await expect(page.locator('select#category-select')).toBeVisible();
    await expect(page.locator('select[name="file_types"]')).toBeVisible();
    await expect(
      page.getByRole('button', { name: 'Search' })
    ).toBeVisible();
  });

  test('search by asset name', async ({ page, testAssets }) => {
    await navigateToSearchPage(page);

    // Search for a specific tag
    await searchByText(page, 'pre_test_asset');
    await submitSearch(page);

    // Verify URL contains search parameter
    await expect(page).toHaveURL(/tag=pre_test_asset/);

    // Verify search results 
    await verifySearchResults(page, true);

    // Verify we found the expected number of assets
    const count = await getSearchResultsCount(page);
    expect(count).toEqual(2);
  });

  test('should filter by asset type', async ({ page, testAssets }) => {
    await navigateToSearchPage(page);
    // To limit the results to our testcase
    await searchByText(page, 'pre_test_asset');

    // Select a specific asset type
    await selectAssetType(page, 'guide');
    await submitSearch(page);

    // Verify URL contains asset_type parameter
    await expect(page).toHaveURL(/asset_type=guide/);

    // Verify the filter is applied
    const assetTypeSelect = page.locator('select[name="asset_type"]');
    await expect(assetTypeSelect).toHaveValue('guide');

    // Verify we found the expected number of assets
    const count = await getSearchResultsCount(page);
    expect(count).toEqual(1);

  });

  test('should filter by category', async ({ page, testAssets }) => {
    await navigateToSearchPage(page);
    // To limit the results to our testcase
    await searchByText(page, 'pre_test_asset');


    // select category
    const categorySelect = page.locator('select#category-select');
    await selectCategory(page, 'partners')
    await submitSearch(page);

    // Verify the filter is applied
    await expect(categorySelect).toHaveValue('partners');

    // Verify the count
    const count = await getSearchResultsCount(page);
    expect(count).toEqual(1);
  })


  test('should clear filters and show all assets', async ({ page, testAssets }) => {
    await navigateToSearchPage(page);

    // First apply some filters
    await searchByText(page, 'test');
    await selectAssetType(page, 'guide');
    await submitSearch(page);

    // Clear filters by selecting "All" options
    await searchByText(page, '');
    await selectAssetType(page, '');
    await selectCategory(page, '');
    await submitSearch(page);

    // Verify URL has no filter parameters
    await expect(
      page.locator('#main-content').filter({ hasText: 'Start a search' })
    ).toBeVisible();
  });

  test('should show no results message for non-existent search', async ({
    page,
    testAssets,
  }) => {
    await navigateToSearchPage(page);

    // Search for something that do not exist
    await searchByText(page, 'veryveryveryvery_random_random_string_string_1234');
    await submitSearch(page);

    // Verify no results message
    await verifySearchResults(page, false);
  });

  test('should persist search filters after page reload', async ({ page, testAssets }) => {
    await navigateToSearchPage(page);

    // Apply filters
    await searchByText(page, 'test');
    await selectAssetType(page, 'guide');
    await submitSearch(page);

    // Get current URL
    const currentUrl = page.url();

    // Reload page
    await page.reload();

    // Verify filters are still applied
    await expect(page.locator('input#tag')).toHaveValue('test');
    await expect(page.locator('select[name="asset_type"]')).toHaveValue(
      'guide'
    );
    await expect(page).toHaveURL(currentUrl);
  });

  test('should navigate to asset details from search results', async ({
    page, testAssets
  }) => {
    await navigateToSearchPage(page);

    // Search for assets
    await searchByText(page, 'test');
    await submitSearch(page);

    // Check if there are any results
    const assetCards = page.locator('.p-asset-card--thumbnail');

    await assetCards.first().click();

    // Verify popup opened with asset content
    await expect(page.locator('#main-content h1')).toHaveText('Asset details');
  });

});