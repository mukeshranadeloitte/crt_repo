const fs = require('fs');
const path = require('path');

const basePath = 'c:\\Users\\mukerana\\Documents\\VS_Code\\github_repo\\crt_repo';

// Create directories
const agentsDir = path.join(basePath, '.github', 'agents');
const promptsDir = path.join(basePath, '.github', 'prompts');

fs.mkdirSync(agentsDir, { recursive: true });
fs.mkdirSync(promptsDir, { recursive: true });

console.log('✓ Created directories:');
console.log('  - .github/agents');
console.log('  - .github/prompts');

// Read source files and copy to destination
const file1Source = path.join(basePath, 'e2e-uat-pipeline.agent.md');
const file1Dest = path.join(agentsDir, 'e2e-uat-pipeline.agent.md');
const file2Source = path.join(basePath, 'create-e2e-uat-pipeline.prompt.md');
const file2Dest = path.join(promptsDir, 'create-e2e-uat-pipeline.prompt.md');

fs.copyFileSync(file1Source, file1Dest);
fs.copyFileSync(file2Source, file2Dest);

console.log('\n✓ Copied files:');
console.log(`  - ${file1Dest}`);
console.log(`  - ${file2Dest}`);

// Verify files
console.log('\n✓ Verification:');
if (fs.existsSync(file1Dest)) {
  const stats1 = fs.statSync(file1Dest);
  console.log(`  File 1: FOUND (${stats1.size} bytes)`);
}
if (fs.existsSync(file2Dest)) {
  const stats2 = fs.statSync(file2Dest);
  console.log(`  File 2: FOUND (${stats2.size} bytes)`);
}

// Show directory structure
console.log('\n✓ Directory Structure:');
const showTree = (dir, prefix = '') => {
  const files = fs.readdirSync(dir);
  files.forEach((file, index) => {
    const fullPath = path.join(dir, file);
    const isLast = index === files.length - 1;
    const connector = isLast ? '└── ' : '├── ';
    console.log(prefix + connector + file);
    
    if (fs.statSync(fullPath).isDirectory() && file !== 'workflows') {
      const nextPrefix = prefix + (isLast ? '    ' : '│   ');
      showTree(fullPath, nextPrefix);
    }
  });
};

showTree(path.join(basePath, '.github'));
