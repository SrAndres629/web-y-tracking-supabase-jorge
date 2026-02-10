/**
 * 📦 ROLLUP CONFIGURATION
 * Bundle JavaScript modules for production
 */

import { nodeResolve } from '@rollup/plugin-node-resolve';
import terser from '@rollup/plugin-terser';

const isProduction = process.env.NODE_ENV === 'production';

export default [
  /* ─────────────────────────────────────────────────────────────────
     BUNDLE 1: Tracking Engine (Core)
     ───────────────────────────────────────────────────────────────── */
  {
    input: 'engines/tracking/index.js',
    output: [
      {
        file: 'dist/js/tracking.modern.js',
        format: 'esm',
        sourcemap: true,
      },
      {
        file: 'dist/js/tracking.legacy.js',
        format: 'umd',
        name: 'TrackingEngine',
        sourcemap: true,
        globals: {
          // No external dependencies
        },
      },
    ],
    plugins: [
      nodeResolve(),
      isProduction && terser({
        compress: {
          drop_console: true,
          drop_debugger: true,
        },
        mangle: true,
      }),
    ].filter(Boolean),
  },

  /* ─────────────────────────────────────────────────────────────────
     BUNDLE 2: UI Engine
     ───────────────────────────────────────────────────────────────── */
  {
    input: 'engines/ui/index.js',
    output: [
      {
        file: 'dist/js/ui.modern.js',
        format: 'esm',
        sourcemap: true,
      },
      {
        file: 'dist/js/ui.legacy.js',
        format: 'umd',
        name: 'UIEngine',
        sourcemap: true,
      },
    ],
    plugins: [
      nodeResolve(),
      isProduction && terser({
        compress: {
          drop_console: false, // Keep console for UI debugging
        },
      }),
    ].filter(Boolean),
  },

  /* ─────────────────────────────────────────────────────────────────
     BUNDLE 3: All Engines (Master)
     ───────────────────────────────────────────────────────────────── */
  {
    input: 'engines/index.js',
    output: [
      {
        file: 'dist/js/engines.bundle.js',
        format: 'esm',
        sourcemap: true,
      },
      {
        file: 'dist/js/engines.bundle.min.js',
        format: 'iife',
        name: 'AppEngines',
        sourcemap: true,
        plugins: [terser()],
      },
    ],
    plugins: [
      nodeResolve(),
    ],
  },

  /* ─────────────────────────────────────────────────────────────────
     BUNDLE 4: Motion Engine (GSAP-dependent)
     ───────────────────────────────────────────────────────────────── */
  {
    input: 'engines/motion/index.js',
    output: {
      file: 'dist/js/motion.modern.js',
      format: 'esm',
      sourcemap: true,
    },
    external: ['gsap', 'lenis'], // External dependencies (CDN)
    plugins: [
      nodeResolve(),
    ],
  },
];
