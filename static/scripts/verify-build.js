#!/usr/bin/env node
/**
 * 🔍 BUILD VERIFICATION SCRIPT
 * Validates that all required files exist and have correct sizes
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

// Expected build outputs
const requiredFiles = [
  // CSS
  { path: 'dist/css/app.min.css', minSize: 50000, description: 'Main CSS bundle' },
  
  // JS
  { path: 'dist/js/engines.bundle.min.js', minSize: 5000, description: 'Engines bundle (minified)' },
  { path: 'dist/js/tracking.modern.js', minSize: 8000, description: 'Tracking module (ESM)' },
  { path: 'dist/js/ui.modern.js', minSize: 3000, description: 'UI module (ESM)' },
];

// ANSI colors
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

function checkFile(fileConfig) {
  const fullPath = path.join(rootDir, fileConfig.path);
  
  if (!fs.existsSync(fullPath)) {
    return {
      ok: false,
      message: `${colors.red}✗ MISSING${colors.reset}: ${fileConfig.path}`,
    };
  }
  
  const stats = fs.statSync(fullPath);
  const size = stats.size;
  
  if (size < fileConfig.minSize) {
    return {
      ok: false,
      message: `${colors.yellow}⚠ SMALL${colors.reset}: ${fileConfig.path} (${formatSize(size)}, expected >${formatSize(fileConfig.minSize)})`,
    };
  }
  
  return {
    ok: true,
    message: `${colors.green}✓ OK${colors.reset}: ${fileConfig.path} (${formatSize(size)})`,
    size,
  };
}

function main() {
  console.log(`${colors.blue}═══════════════════════════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.blue}  BUILD VERIFICATION${colors.reset}`);
  console.log(`${colors.blue}═══════════════════════════════════════════════════════════════${colors.reset}`);
  console.log();
  
  let passed = 0;
  let failed = 0;
  
  for (const file of requiredFiles) {
    const result = checkFile(file);
    console.log(`  ${result.message}`);
    
    if (result.ok) {
      passed++;
    } else {
      failed++;
    }
  }
  
  console.log();
  console.log(`${colors.blue}───────────────────────────────────────────────────────────────${colors.reset}`);
  console.log(`  Total: ${passed + failed} files | ${colors.green}${passed} passed${colors.reset} | ${colors.red}${failed} failed${colors.reset}`);
  
  if (failed > 0) {
    console.log();
    console.log(`${colors.red}  Build verification FAILED${colors.reset}`);
    process.exit(1);
  } else {
    console.log();
    console.log(`${colors.green}  ✓ All builds verified successfully!${colors.reset}`);
    process.exit(0);
  }
}

main();
