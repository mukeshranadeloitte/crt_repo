#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Change to target directory
process.chdir('c:\\Users\\mukerana\\Documents\\VS_Code\\github_repo\\crt_repo');

try {
  // 1. Create directories
  console.log('Step 1: Creating directories...');
  fs.mkdirSync('.github\\agents', { recursive: true });
  fs.mkdirSync('.github\\prompts', { recursive: true });
  console.log('✓ Directories created\n');

  // 2. Copy files
  console.log('Step 2: Copying files...');
  fs.copyFileSync('e2e-uat-pipeline.agent.md', '.github\\agents\\e2e-uat-pipeline.agent.md');
  fs.copyFileSync('create-e2e-uat-pipeline.prompt.md', '.github\\prompts\\create-e2e-uat-pipeline.prompt.md');
  console.log('✓ Files copied\n');

  // 3. Verify files exist and show sizes
  console.log('Step 3: Verifying destination files and sizes:');
  const file1 = '.github\\agents\\e2e-uat-pipeline.agent.md';
  const file2 = '.github\\prompts\\create-e2e-uat-pipeline.prompt.md';

  if (fs.existsSync(file1)) {
    const stat1 = fs.statSync(file1);
    console.log(`  ✓ ${file1} - ${stat1.size} bytes`);
  } else {
    console.log(`  ✗ ${file1} - NOT FOUND`);
  }

  if (fs.existsSync(file2)) {
    const stat2 = fs.statSync(file2);
    console.log(`  ✓ ${file2} - ${stat2.size} bytes`);
  } else {
    console.log(`  ✗ ${file2} - NOT FOUND`);
  }

  // 4. Show directory structure of .github
  console.log('\nStep 4: Directory structure of .github:\n');
  const showTree = (dir, prefix = '') => {
    try {
      const items = fs.readdirSync(dir, { withFileTypes: true });
      items.sort((a, b) => a.name.localeCompare(b.name));
      
      items.forEach((item, index) => {
        const isLast = index === items.length - 1;
        const connector = isLast ? '└── ' : '├── ';
        const fullPath = path.join(dir, item.name);
        
        if (item.isDirectory()) {
          console.log(prefix + connector + item.name + '/');
          const nextPrefix = prefix + (isLast ? '    ' : '│   ');
          showTree(fullPath, nextPrefix);
        } else {
          const stat = fs.statSync(fullPath);
          console.log(prefix + connector + item.name + ` (${stat.size} bytes)`);
        }
      });
    } catch (err) {
      console.log(prefix + '└── [Error reading directory]');
    }
  };

  showTree('.github');

  console.log('\n✓ SUCCESS: All tasks completed!');
} catch (error) {
  console.error('\n✗ ERROR:', error.message);
  process.exit(1);
}
