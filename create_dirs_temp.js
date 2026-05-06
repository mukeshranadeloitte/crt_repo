const fs = require('fs');
const path = require('path');

const dirs = [
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

const baseDir = 'c:\\Users\\mukerana\\Documents\\VS_Code\\github_repo\\crt_repo';
let created = 0;

dirs.forEach(dir => {
    const fullPath = path.join(baseDir, dir);
    if (!fs.existsSync(fullPath)) {
        fs.mkdirSync(fullPath, { recursive: true });
        created++;
    }
});

console.log('Created ' + created + ' directories successfully');
process.exit(0);
