import { test as base, Page } from '@playwright/test';
import path from 'path';

type TestAssets = {
    asset1: { name: string; type: string; tags: string[] };
    asset2: { name: string; type: string; tags: string[] };
};

type WorkerFixtures = {
    testAssets: TestAssets;
};

// Fixture to create assets before search
export const test = base.extend<{}, WorkerFixtures>({
    testAssets: [async ({ browser }, use) => {
        // Create a new page for setup
        const context = await browser.newContext();
        const page = await context.newPage();
        console.log('Creating test assets (runs once for all tests)...');

        const assets: TestAssets = {
            asset1: {
                name: 'pre_test_asset_1',
                type: 'guide',
                tags: ['e2e-search-test', 'test'],
            },
            asset2: {
                name: 'pre_test_asset_2',
                type: 'image',
                tags: ['e2e-search-test', 'image-test'],
            },
        };

        // Create first test asset
        await createAsset(page, {
            fileName: 'pre_test_asset_1.txt',
            assetType: 'guide',
            assetName: assets.asset1.name,
            productTagSearch: 'digital',
            productTagLabel: 'Digital Signage',
            customTags: assets.asset1.tags,
            language: 'English',
        });

        console.log(`Created ${assets.asset1.name}`);

        // Create second test asset
        await createAsset(page, {
            fileName: 'pre_test_asset_2.txt',
            assetType: 'image',
            assetName: assets.asset2.name,
            productTagSearch: 'amd',
            productTagLabel: 'amd',
            customTags: assets.asset2.tags,
            language: 'Chinese',
        });
        use(assets)
        console.log(`Created ${assets.asset2.name}`);

        await context.close();
    }, { scope: 'worker' }],
});

export { expect } from '@playwright/test';

// Helper function to create an asset
async function createAsset(
    page: Page,
    options: {
        fileName: string;
        assetType: string;
        assetName: string;
        productTagSearch: string;
        productTagLabel: string;
        customTags: string[];
        language: string;
    }
) {
    await page.goto('/manager/create');

    // Upload file
    const filePath = path.resolve(__dirname, `../test_upload_files/${options.fileName}`);
    await page
        .getByRole('button', { name: 'Choose files to upload' })
        .setInputFiles(filePath);

    // Set asset type
    await page.locator('#asset-type-select').selectOption(options.assetType);

    // Set asset name
    await page.getByRole('textbox', { name: 'Asset name' }).fill(options.assetName);

    // Add product tag
    const productTagInput = page.getByRole('textbox', {
        name: 'Product or category tags',
    });
    await productTagInput.click();
    await productTagInput.fill(options.productTagSearch);
    await page.getByRole('button', { name: options.productTagLabel }).click();
    await page.locator('html').click();

    // Add custom tags
    const customTagInput = page.getByRole('textbox', {
        name: 'Enter tag and press enter',
    });
    for (const tag of options.customTags) {
        await customTagInput.click();
        await customTagInput.fill(tag);
        await customTagInput.press('Enter');
    }

    // Set language
    await page.getByLabel('language').selectOption(options.language);

    // Submit
    await page.getByRole('button', { name: 'Upload asset' }).click();

    // Wait for completion
    await page.waitForSelector('h1:has-text("Upload complete")', {
        timeout: 1000000,
    });
}
