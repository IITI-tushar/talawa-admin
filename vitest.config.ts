import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { nodePolyfills } from 'vite-plugin-node-polyfills';
import tsconfigPaths from 'vite-tsconfig-paths';
import svgrPlugin from 'vite-plugin-svgr';

export default defineConfig({
  plugins: [
    react(),
    nodePolyfills({
      include: ['events'],
    }),
    tsconfigPaths(),
    svgrPlugin(),
  ],
  test: {
    include: [
      'C:/Tushar_CODES/Open source/talawa-admin/src/screens/UserPortal/Settings/Settings.test.tsx',
    ],
    globals: true,
    environment: 'jsdom',
    setupFiles: 'vitest.setup.ts',
    coverage: {
      enabled: true,
      provider: 'v8',
      reportsDirectory: './coverage/vitest',
      exclude: [
        'node_modules',
        'dist',
        // '**/*.{test}.{js,jsx,ts,tsx}',
        'coverage/**',
        '**/index.{js,ts}',
        '**/*.d.ts',
        'src/test/**',
        'vitest.config.ts',
      ],
      reporter: ['text', 'html', 'text-summary', 'lcov'],
    },
  },
});
