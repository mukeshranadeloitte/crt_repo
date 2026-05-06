const fs = require('fs');
const path = require('path');

const basePath = 'c:\\Users\\mukerana\\Documents\\VS_Code\\github_repo\\crt_repo';

// Define all directories to create
const directories = [
  '.github\\agents',
  '.github\\instructions',
  '.github\\skills\\sf-static-analysis',
  '.github\\skills\\sf-security',
  '.github\\skills\\sf-code-quality',
  '.github\\skills\\sf-architecture',
  '.github\\skills\\sf-data-model',
  '.github\\skills\\sf-governor-performance',
  '.github\\skills\\sf-test-quality',
  '.github\\skills\\sf-api-versioning',
  '.github\\skills\\sf-deployment',
  '.github\\skills\\sf-build-forms',
  '.github\\skills\\sf-event-driven',
  '.github\\skills\\sf-web-app-security',
  '.github\\skills\\sf-auth-session-security',
  '.github\\skills\\sf-shield-encryption',
  '.github\\skills\\sf-audit-monitoring',
  '.github\\skills\\sf-resilience',
  '.github\\skills\\sf-experience-cloud-security',
  '.github\\skills\\sf-package-review'
];

console.log('Creating directories...\n');

let createdCount = 0;
let alreadyExistCount = 0;

// Create each directory
directories.forEach((dir) => {
  const fullPath = path.join(basePath, dir);
  try {
    if (!fs.existsSync(fullPath)) {
      fs.mkdirSync(fullPath, { recursive: true });
      console.log(`✓ Created: ${dir}`);
      createdCount++;
    } else {
      console.log(`✓ Already exists: ${dir}`);
      alreadyExistCount++;
    }
  } catch (err) {
    console.log(`✗ Error creating ${dir}: ${err.message}`);
  }
});

console.log(`\n--- Verification ---\n`);
console.log(`Verifying all directories exist:\n`);

let allExist = true;
directories.forEach((dir) => {
  const fullPath = path.join(basePath, dir);
  if (fs.existsSync(fullPath)) {
    console.log(`✓ ${dir}`);
  } else {
    console.log(`✗ ${dir} (MISSING)`);
    allExist = false;
  }
});

console.log(`\n--- Summary ---`);
console.log(`Created: ${createdCount}`);
console.log(`Already existed: ${alreadyExistCount}`);
console.log(`Total: ${directories.length}`);

if (allExist) {
  console.log(`\n✓ All ${directories.length} directories created successfully!`);
} else {
  console.log(`\n✗ Some directories are missing`);
  process.exit(1);
}
