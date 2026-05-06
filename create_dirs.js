const fs = require('fs');
const path = require('path');

const basePath = 'c:\\Users\\mukerana\\Documents\\VS_Code\\github_repo\\crt_repo';

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

let created = 0;
let errors = 0;

directories.forEach(dir => {
    try {
        const fullPath = path.join(basePath, dir);
        fs.mkdirSync(fullPath, { recursive: true });
        created++;
    } catch (err) {
        console.error(`Error creating ${dir}:`, err.message);
        errors++;
    }
});

console.log(`Successfully created ${created} directories`);
if (errors > 0) {
    console.log(`Errors: ${errors}`);
    process.exit(1);
}
