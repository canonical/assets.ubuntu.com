import { test as base } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

type TempFilesFixture = {
    tempFiles: {
        createFile: (fileName: string, content: string) => string;
        getFilePath: (fileName: string) => string;
        cleanup: () => void;
    };
};

// Worker-scoped fixture for creating temporary test files
export const test = base.extend<TempFilesFixture>({
    tempFiles: async ({}, use) => {
        const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'playwright-test-'));
        const createdFiles: string[] = [];

        const fixture = {
            /**
             * @param fileName - Name of the file to create
             * @param content - Content to write to the file
             * @returns Full path to the created file
             */
            createFile: (fileName: string, content: string): string => {
                const filePath = path.join(tempDir, fileName);
                fs.writeFileSync(filePath, content, 'utf-8');
                createdFiles.push(filePath);
                return filePath;
            },

            /**
             * @param fileName - Name of the file
             * @returns Full path to the file
             */
            getFilePath: (fileName: string): string => {
                return path.join(tempDir, fileName);
            },

            /**
             * Cleanup all created files and the temp directory
             */
            cleanup: (): void => {
                createdFiles.forEach((filePath) => {
                    if (fs.existsSync(filePath)) {
                        fs.unlinkSync(filePath);
                    }
                });
                if (fs.existsSync(tempDir)) {
                    fs.rmdirSync(tempDir);
                }
            },
        };

        await use(fixture);

        fixture.cleanup();
    },
});

export { expect } from '@playwright/test';

/**
 * Helper function to create multiple test files at once
 * @param tempFiles - The tempFiles fixture
 * @param files - Object mapping file names to their content
 * @returns Object mapping file names to their full paths
 */
export function createTestFiles(
    tempFiles: TempFilesFixture['tempFiles'],
    files: Record<string, string>
): Record<string, string> {
    const filePaths: Record<string, string> = {};
    
    for (const [fileName, content] of Object.entries(files)) {
        filePaths[fileName] = tempFiles.createFile(fileName, content);
    }
    
    return filePaths;
}
