// BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
// Jest configuration for Next.js 14 + TypeScript.
// Requires packages: jest jest-environment-jsdom @testing-library/react @testing-library/jest-dom
// Install with: pnpm add -D jest jest-environment-jsdom @testing-library/react @testing-library/jest-dom @types/jest

const nextJest = require('next/jest');

const createJestConfig = nextJest({
  // Path to your Next.js app to load next.config.js and .env files
  dir: './',
});

/** @type {import('jest').Config} */
const config = {
  testEnvironment: 'jest-environment-jsdom',

  // Match test files
  testMatch: [
    '**/__tests__/**/*.{ts,tsx}',
    '**/*.{test,spec}.{ts,tsx}',
  ],

  // Exclude e2e tests (Playwright handles those)
  testPathIgnorePatterns: [
    '/node_modules/',
    '/.next/',
    '/e2e/',
  ],

  // Resolve @/ alias (mirrors tsconfig.json paths)
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },

  // Setup files for @testing-library/jest-dom matchers
  setupFilesAfterFramework: [],

  // Coverage thresholds (KR-041: 80% minimum)
  coverageThreshold: {
    global: {
      lines: 80,
      branches: 80,
      functions: 80,
      statements: 80,
    },
  },

  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/index.ts',
    '!src/app/**/layout.tsx',
    '!src/app/**/page.tsx',
  ],
};

module.exports = createJestConfig(config);
