#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const basePath = path.resolve(__dirname);

const directories = [
    '.github/agents',
    '.github/instructions',
    '.github/skills/sf-static-analysis',
    '.github/skills/sf-security',
    '.github/skills/sf-code-quality',
    '.github/skills/sf-architecture',
    '.github/skills/sf-data-model',
    '.github/skills/sf-governor-performance',
    '.github/skills/sf-test-quality',
    '.github/skills/sf-api-versioning',
    '.github/skills/sf-deployment',
    '.github/skills/sf-build-forms',
    '.github/skills/sf-event-driven',
    '.github/skills/sf-web-app-security',
    '.github/skills/sf-auth-session-security',
    '.github/skills/sf-shield-encryption',
    '.github/skills/sf-audit-monitoring',
    '.github/skills/sf-resilience',
    '.github/skills/sf-experience-cloud-security',
    '.github/skills/sf-package-review'
];

console.log(`Base path: ${basePath}`);
console.log(`Creating ${directories.length} directories...\n`);

let created = 0;
let errors = [];

directories.forEach(dir => {
    try {
        const fullPath = path.join(basePath, dir);
        if (!fs.existsSync(fullPath)) {
            fs.mkdirSync(fullPath, { recursive: true });
            created++;
            console.log(`✓ Created: ${dir}`);
        } else {
            console.log(`→ Already exists: ${dir}`);
        }
    } catch (err) {
        errors.push({dir, error: err.message});
        console.error(`✗ Error creating ${dir}: ${err.message}`);
    }
});

console.log(`\n${created} new directories created`);
if (errors.length > 0) {
    console.log(`${errors.length} errors encountered`);
    process.exit(1);
}

// Now create .gitkeep files in each directory
console.log(`\nCreating .gitkeep files...\n`);

let gitkeepCreated = 0;
directories.forEach(dir => {
    try {
        const fullPath = path.join(basePath, dir, '.gitkeep');
        fs.writeFileSync(fullPath, '');
        gitkeepCreated++;
        console.log(`✓ Created: ${dir}/.gitkeep`);
    } catch (err) {
        console.error(`✗ Error creating .gitkeep in ${dir}: ${err.message}`);
    }
});

console.log(`\n${gitkeepCreated} .gitkeep files created`);
console.log('\n✓ Setup complete!');
