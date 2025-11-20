import { test, expect } from './fixtures/temp-files.fixture';
import { Page, Locator } from '@playwright/test';

async function navigateToCreatePage(page: Page) {
    await page.goto('/manager/create');
}

async function uploadFiles(page: Page, filePaths: string[]) {
    const uploadButton = page.getByRole('button', {
        name: 'Choose files to upload',
    });
    await uploadButton.setInputFiles(filePaths);
}

async function fillAssetMetadata(
    page: Page,
    options: {
        assetType: string;
        assetName: string;
        productSearch: string;
        productTagLabel: string;
        customTags: string[];
        language: string;
    }
) {
    // Select asset type
    await page.locator('#asset-type-select').selectOption(options.assetType);

    // Fill asset name
    const assetNameInput = page.getByRole('textbox', { name: 'Asset name' });
    await assetNameInput.fill(options.assetName);

    // Add and verify product tag
    const productTagInput = page.getByRole('textbox', {
        name: 'Product or category tags',
    });
    await productTagInput.click();
    await productTagInput.fill(options.productSearch);
    await page.getByRole('button', { name: options.productTagLabel }).click();
    await expect(page.locator('#create-update-asset')).toContainText(
        options.productTagLabel
    );
    await page.locator('html').click();

    // Add custom tags
    const customTagInput = page.getByRole('textbox', {
        name: 'Enter tag and press enter',
    });
    for (const tag of options.customTags) {
        await customTagInput.click();
        await customTagInput.fill(tag);
        await customTagInput.press('Enter');
        await expect(page.locator('#create-update-asset')).toContainText(tag);
    }

    // Select language
    await page.getByLabel('language').selectOption(options.language);
}

async function submitUpload(page: Page) {
    await page.getByRole('button', { name: 'Upload asset' }).click();
    await expect(
        page.getByRole('heading', { name: 'Upload complete' })
    ).toBeVisible();
}

async function verifyAssetContent(page: Page, pageElement: Locator, expectedText: string) {
    const popupPromise = page.waitForEvent('popup');
    await pageElement.click();
    const popup = await popupPromise;
    await expect(popup.locator('pre')).toContainText(expectedText);
    await popup.close();
}

test.describe('Asset creation flow', () => {
    test('single asset creation', async ({ page, tempFiles }) => {
        // Create temporary test file
        const file1Path = tempFiles.createFile('test_upload_1.txt', 'test upload 1');
        
        await navigateToCreatePage(page);

        // Upload single file
        await uploadFiles(page, [file1Path]);

        // Fill metadata
        await fillAssetMetadata(page, {
            assetType: 'guide',
            assetName: 'test_asset',
            productSearch: 'digital',
            productTagLabel: 'Digital Signage',
            customTags: ['single-upload', 'e2e'],
            language: 'Chinese',
        });

        // Submit and verify
        await submitUpload(page);
        const assetCard = page.locator('.p-card__content')
        await expect(assetCard).toContainText('test_asset');
        await expect(assetCard).toContainText(
            'digital-signage'
        );
        await expect(assetCard).toContainText(
            'e2e'
        );
        await expect(assetCard).toContainText(
            'single-upload'
        );
        await expect(assetCard).toContainText(
            'Language: Chinese'
        );
        const assetCardThumbnail = page.locator('.p-asset-card--thumbnail')
        await verifyAssetContent(page, assetCardThumbnail, 'test upload 1');
    });

    test('multiple assets creation', async ({ page, tempFiles }) => {
        // Create temporary test files
        const file2Path = tempFiles.createFile('test_upload_2.txt', 'test upload 2');
        const file3Path = tempFiles.createFile('test_upload_3.txt', 'test upload 3');
        
        await navigateToCreatePage(page);

        // Upload multiple files
        await uploadFiles(page, [file2Path, file3Path]);

        // Fill metadata
        await fillAssetMetadata(page, {
            assetType: 'guide',
            assetName: 'multi_test_asset',
            productSearch: 'amd',
            productTagLabel: 'AMD',
            customTags: ['multi-upload', 'e2e'],
            language: 'English',
        });

        // Submit and verify
        await submitUpload(page);

        const firstCard = page.locator('.p-card__content').first();
        await expect(firstCard).toContainText('multi_test_asset');
        await expect(firstCard).toContainText('e2e');
        await expect(firstCard).toContainText('amd');
        await expect(firstCard).toContainText('multi-upload');

        // Verify correct number of asset cards
        const assetCards = page.locator('.p-asset-card--thumbnail');
        await expect(assetCards).toHaveCount(2);

        // Verify first asset content
        await verifyAssetContent(page, assetCards.first(), 'test upload 2');


        // Verify second asset content
        await verifyAssetContent(page, assetCards.nth(1), 'test upload 3');
    });
});
