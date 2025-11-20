import { test as base, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

type TestAssets = {
    asset1: { name: string; type: string; tags: string[] };
    asset2: { name: string; type: string; tags: string[] };
};

type WorkerFixtures = {
    testAssets: TestAssets;
};

// Temp directory for worker-scoped file generation
let workerTempDir: string | null = null;

function ensureTempDir(): string {
    if (!workerTempDir) {
        workerTempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'playwright-worker-'));
    }
    return workerTempDir;
}

function createTempFile(fileName: string, content: string): string {
    const tempDir = ensureTempDir();
    const filePath = path.join(tempDir, fileName);
    fs.writeFileSync(filePath, content, 'utf-8');
    return filePath;
}

function cleanupTempDir(): void {
    if (workerTempDir && fs.existsSync(workerTempDir)) {
        const files = fs.readdirSync(workerTempDir);
        files.forEach((file) => {
            fs.unlinkSync(path.join(workerTempDir!, file));
        });
        fs.rmdirSync(workerTempDir);
        workerTempDir = null;
    }
}

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

        // Create temporary test files
        const file1Path = createTempFile('pre_test_asset_1.txt', 'pre test asset 1 content');
        const file2Path = createTempFile('pre_test_asset_2.txt', 'pre test asset 2 content');

        // Create first test asset
        await createAsset(page, {
            filePath: file1Path,
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
            filePath: file2Path,
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
        
        // Cleanup temporary files
        cleanupTempDir();
    }, { scope: 'worker' }],
});

export { expect } from '@playwright/test';

// Helper function to create an asset
async function createAsset(
    page: Page,
    options: {
        filePath: string;
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
    await page
        .getByRole('button', { name: 'Choose files to upload' })
        .setInputFiles(options.filePath);

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
