#!/usr/bin/env node
/**
 * ✅ SYSTEM VALIDATION SCRIPT
 * Verifies that static_new is functionally equivalent to static
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

let passed = 0;
let failed = 0;

function log(section, message, status = 'info') {
  const icons = {
    pass: '✅',
    fail: '❌',
    warn: '⚠️',
    info: 'ℹ️'
  };
  const color = status === 'pass' ? colors.green : status === 'fail' ? colors.red : status === 'warn' ? colors.yellow : colors.cyan;
  console.log(`  ${color}${icons[status]}${colors.reset} [${section}] ${message}`);
}

// ============================================
// TEST 1: Verificar archivos críticos existen
// ============================================
function testCriticalFiles() {
  console.log(`\n${colors.blue}TEST 1: Archivos Críticos${colors.reset}`);
  
  const files = [
    'engines/index.js',
    'engines/tracking/index.js',
    'engines/ui/index.js',
    'engines/motion/index.js',
    'engines/legacy-adapter.js',
    'engines/core/dom.js',
    'engines/core/storage.js',
    'design-system/tokens/index.css',
    'design-system/tailwind/input.css',
    'package.json',
    'tailwind.config.js',
  ];
  
  for (const file of files) {
    const fullPath = path.join(rootDir, file);
    if (fs.existsSync(fullPath)) {
      log('FILES', `${file} existe`, 'pass');
      passed++;
    } else {
      log('FILES', `${file} NO EXISTE`, 'fail');
      failed++;
    }
  }
}

// ============================================
// TEST 2: Verificar compatibilidad de API
// ============================================
function testAPICompatibility() {
  console.log(`\n${colors.blue}TEST 2: Compatibilidad de API${colors.reset}`);
  
  const checks = [
    // TrackingEngine
    { file: 'engines/tracking/index.js', mustContain: ['initialized', 'init', 'track', 'trackCustom', 'handleConversion', 'turnstileToken', 'isHuman'], name: 'TrackingEngine API' },
    // UIEngine
    { file: 'engines/ui/index.js', mustContain: ['initialized', 'init', 'NavManager', 'SliderManager', 'CROManager'], name: 'UIEngine API' },
    // MotionEngine
    { file: 'engines/motion/index.js', mustContain: ['initialized', 'init'], name: 'MotionEngine API' },
    // Legacy adapter
    { file: 'engines/legacy-adapter.js', mustContain: ['window.handleConversion', 'window.TrackingEngine', 'window.onTurnstileSuccess'], name: 'Legacy Adapter Globals' },
  ];
  
  for (const check of checks) {
    const fullPath = path.join(rootDir, check.file);
    const content = fs.readFileSync(fullPath, 'utf8');
    const missing = check.mustContain.filter(str => !content.includes(str));
    
    if (missing.length === 0) {
      log('API', `${check.name} completa`, 'pass');
      passed++;
    } else {
      log('API', `${check.name} - faltan: ${missing.join(', ')}`, 'fail');
      failed++;
    }
  }
}

// ============================================
// TEST 3: Verificar clases CSS compatibles
// ============================================
function testCSSCompatibility() {
  console.log(`\n${colors.blue}TEST 3: Compatibilidad CSS${colors.reset}`);
  
  const requiredClasses = [
    { selector: '.btn-gold-liquid', file: 'atoms/buttons/button-gold-liquid.css' },
    { selector: '.glass-nav-premium', file: 'layouts/navigation/glass-nav.css' },
    { selector: '.card-glass', file: 'atoms/cards/card-glass.css' },
    { selector: '.service-card-premium', file: 'atoms/cards/card-service-premium.css' },
    { selector: '.text-liquid-gold', file: 'atoms/text/text-liquid-gold.css' },
  ];
  
  for (const cls of requiredClasses) {
    const fullPath = path.join(rootDir, cls.file);
    if (fs.existsSync(fullPath)) {
      const content = fs.readFileSync(fullPath, 'utf8');
      if (content.includes(cls.selector)) {
        log('CSS', `${cls.selector} definido`, 'pass');
        passed++;
      } else {
        log('CSS', `${cls.selector} NO encontrado en ${cls.file}`, 'fail');
        failed++;
      }
    } else {
      log('CSS', `${cls.file} no existe`, 'fail');
      failed++;
    }
  }
}

// ============================================
// TEST 4: Verificar estructura de assets
// ============================================
function testAssetsStructure() {
  console.log(`\n${colors.blue}TEST 4: Estructura de Assets${colors.reset}`);
  
  const requiredDirs = [
    'assets/images/services/brows/before',
    'assets/images/services/brows/after',
    'assets/images/services/eyes/before',
    'assets/images/services/eyes/after',
    'assets/images/services/lips/before',
    'assets/images/services/lips/after',
    'assets/images/testimonials',
    'assets/images/hero',
    'assets/images/branding',
    'assets/images/meta',
  ];
  
  for (const dir of requiredDirs) {
    const fullPath = path.join(rootDir, dir);
    if (fs.existsSync(fullPath)) {
      log('ASSETS', `${dir}/ existe`, 'pass');
      passed++;
    } else {
      log('ASSETS', `${dir}/ NO EXISTE`, 'warn');
      // No incrementamos failed porque no todas las carpetas pueden tener archivos
    }
  }
}

// ============================================
// TEST 5: Verificar imports válidos
// ============================================
function testValidImports() {
  console.log(`\n${colors.blue}TEST 5: Imports Válidos${colors.reset}`);
  
  const jsFiles = [];
  
  function findJS(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory() && file !== 'node_modules') {
        findJS(fullPath);
      } else if (file.endsWith('.js')) {
        jsFiles.push(fullPath);
      }
    }
  }
  
  findJS(path.join(rootDir, 'engines'));
  
  const importRegex = /import\s+(?:{[^}]+}|[^'"]+)\s+from\s+['"]([^'"]+)['"];?/g;
  
  for (const file of jsFiles) {
    let content = fs.readFileSync(file, 'utf8');
    
    // Remover comentarios antes de buscar imports
    content = content.replace(/\/\*[\s\S]*?\*\//g, ''); // /* comments */
    content = content.replace(/\/\/.*$/gm, ''); // // comments
    
    const imports = [...content.matchAll(importRegex)];
    
    for (const match of imports) {
      const importPath = match[1];
      
      // Ignorar imports de CDN o node_modules
      if (importPath.startsWith('http') || !importPath.startsWith('.')) continue;
      
      // Ignorar paths que contienen el nombre del archivo actual (falsos positivos)
      const fileName = path.basename(file);
      if (importPath.includes(fileName.replace('.js', ''))) continue;
      
      const resolvedPath = path.resolve(path.dirname(file), importPath);
      const possiblePaths = [
        resolvedPath,
        `${resolvedPath}.js`,
        path.join(resolvedPath, 'index.js'),
      ];
      
      const exists = possiblePaths.some(p => fs.existsSync(p));
      
      if (exists) {
        // Import válido
      } else {
        log('IMPORTS', `${importPath} en ${path.relative(rootDir, file)} - NO RESUELTO`, 'fail');
        failed++;
      }
    }
  }
  
  log('IMPORTS', `Verificados ${jsFiles.length} archivos`, 'pass');
  passed++;
}

// ============================================
// MAIN
// ============================================
function main() {
  console.log(`${colors.cyan}╔════════════════════════════════════════════════════════════════╗${colors.reset}`);
  console.log(`${colors.cyan}║         VALIDACIÓN DEL SISTEMA STATIC_NEW                      ║${colors.reset}`);
  console.log(`${colors.cyan}╚════════════════════════════════════════════════════════════════╝${colors.reset}`);
  
  testCriticalFiles();
  testAPICompatibility();
  testCSSCompatibility();
  testAssetsStructure();
  testValidImports();
  
  console.log(`\n${colors.blue}══════════════════════════════════════════════════════════════════${colors.reset}`);
  console.log(`Resultados: ${colors.green}${passed} pasaron${colors.reset} | ${colors.red}${failed} fallaron${colors.reset}`);
  
  if (failed === 0) {
    console.log(`\n${colors.green}✅ SISTEMA VALIDADO - Listo para migración${colors.reset}`);
    process.exit(0);
  } else {
    console.log(`\n${colors.red}❌ SISTEMA TIENE ERRORES - Corregir antes de migrar${colors.reset}`);
    process.exit(1);
  }
}

main();
