#!/usr/bin/env node
/**
 * 🔄 TEMPLATE MIGRATION SCRIPT
 * Updates templates to use new static paths
 * 
 * Usage: node scripts/migrate-templates.js [templates_dir]
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const REPLACEMENTS = [
  // CSS
  {
    from: /\/static\/css\/output\.css/g,
    to: '/static/dist/css/app.min.css',
    description: 'Main CSS bundle'
  },
  {
    from: /\/static\/css\/components\/ba-slider\.css/g,
    to: '/static/molecules/ba-slider/ba-slider.css',
    description: 'BA Slider component CSS'
  },
  
  // JS - Legacy mode (recommended for gradual migration)
  {
    from: /<script[^>]*src="\/static\/js\/tracking\.js"[^>]*><\/script>/g,
    to: '<script type="module" src="/static/engines/legacy-adapter.js"></script>',
    description: 'Tracking/Engines (legacy adapter)'
  },
  {
    from: /<script[^>]*src="\/static\/js\/ui\.js"[^>]*><\/script>/g,
    to: '',
    description: 'UI JS (eliminado - incluido en legacy-adapter)'
  },
  {
    from: /<script[^>]*src="\/static\/js\/motion\.js"[^>]*><\/script>/g,
    to: '',
    description: 'Motion JS (eliminado - incluido en legacy-adapter)'
  },
  
  // Images
  {
    from: /\/static\/images\/brows_(before|after)([^"']*)\.(webp|png)/g,
    to: '/static/assets/images/services/brows/$1/brows_$1$2.$3',
    description: 'Brows service images'
  },
  {
    from: /\/static\/images\/eyes_(before|after)([^"']*)\.(webp|png)/g,
    to: '/static/assets/images/services/eyes/$1/eyes_$1$2.$3',
    description: 'Eyes service images'
  },
  {
    from: /\/static\/images\/lips_(before|after)([^"']*)\.(webp|png)/g,
    to: '/static/assets/images/services/lips/$1/lips_$1$2.$3',
    description: 'Lips service images'
  },
  {
    from: /\/static\/images\/testimonial_(\d+)\.(webp|png)/g,
    to: '/static/assets/images/testimonials/testimonial_$1.$2',
    description: 'Testimonial images'
  },
  {
    from: /\/static\/images\/jorge_hero_([^"']*)\.(webp|png)/g,
    to: '/static/assets/images/hero/jorge_hero_$1.$2',
    description: 'Hero images'
  },
  {
    from: /\/static\/images\/luxury_logo\.svg/g,
    to: '/static/assets/images/branding/luxury_logo.svg',
    description: 'Logo'
  },
  {
    from: /\/static\/images\/og-image\.webp/g,
    to: '/static/assets/images/meta/og-image.webp',
    description: 'OG Image'
  },
  {
    from: /\/static\/images\/microblading_(before|after)([^"']*)\.(webp|png)/g,
    to: '/static/assets/images/services/brows/$1/microblading_$1$2.$3',
    description: 'Microblading images'
  },
  {
    from: /\/static\/images\/lips_after_clean\.(webp|png)/g,
    to: '/static/assets/images/services/lips/after/lips_after_clean.$1',
    description: 'Lips after clean'
  },
];

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function findTemplates(dir) {
  const templates = [];
  
  function scan(directory) {
    const files = fs.readdirSync(directory);
    
    for (const file of files) {
      const fullPath = path.join(directory, file);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        scan(fullPath);
      } else if (file.endsWith('.html')) {
        templates.push(fullPath);
      }
    }
  }
  
  scan(dir);
  return templates;
}

function migrateFile(filePath, dryRun = true) {
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;
  const changes = [];
  
  for (const replacement of REPLACEMENTS) {
    const matches = content.match(replacement.from);
    if (matches) {
      changes.push({
        description: replacement.description,
        count: matches.length,
        example: matches[0]
      });
      
      if (!dryRun) {
        content = content.replace(replacement.from, replacement.to);
      }
      modified = true;
    }
  }
  
  if (!dryRun && modified) {
    fs.writeFileSync(filePath, content, 'utf8');
  }
  
  return { modified, changes };
}

function main() {
  const templatesDir = process.argv[2] || '../templates';
  const dryRun = !process.argv.includes('--apply');
  
  console.log(`${colors.blue}═══════════════════════════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.blue}  TEMPLATE MIGRATION${colors.reset}`);
  console.log(`${colors.blue}═══════════════════════════════════════════════════════════════${colors.reset}`);
  console.log();
  console.log(`  Templates directory: ${templatesDir}`);
  console.log(`  Mode: ${dryRun ? colors.yellow + 'DRY RUN' + colors.reset : colors.red + 'APPLY CHANGES' + colors.reset}`);
  console.log();
  
  // Find templates
  let templates;
  try {
    templates = findTemplates(templatesDir);
  } catch (e) {
    console.error(`${colors.red}Error:${colors.reset} Could not read templates directory: ${e.message}`);
    process.exit(1);
  }
  
  console.log(`  Found ${templates.length} template files`);
  console.log();
  
  let totalFiles = 0;
  let totalChanges = 0;
  
  for (const template of templates) {
    const relativePath = path.relative(templatesDir, template);
    const result = migrateFile(template, dryRun);
    
    if (result.modified) {
      totalFiles++;
      console.log(`${colors.cyan}📄 ${relativePath}${colors.reset}`);
      
      for (const change of result.changes) {
        console.log(`   ${colors.green}✓${colors.reset} ${change.description}: ${change.count} occurrence(s)`);
        totalChanges += change.count;
      }
      console.log();
    }
  }
  
  console.log(`${colors.blue}───────────────────────────────────────────────────────────────${colors.reset}`);
  console.log(`  Files to modify: ${totalFiles}`);
  console.log(`  Total changes: ${totalChanges}`);
  console.log();
  
  if (dryRun) {
    console.log(`${colors.yellow}  ⚠ This was a dry run. No files were modified.${colors.reset}`);
    console.log(`  Run with --apply to apply changes:`);
    console.log(`  node scripts/migrate-templates.js ${templatesDir} --apply`);
  } else {
    console.log(`${colors.green}  ✓ Changes applied successfully!${colors.reset}`);
  }
  console.log();
}

main();
