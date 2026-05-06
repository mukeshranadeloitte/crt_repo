import os
import sys

dirs = [
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
]

base_dir = r'c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo'
os.chdir(base_dir)

created = 0
for dir_path in dirs:
    full_path = os.path.join(base_dir, dir_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path, exist_ok=True)
        created += 1

print(f'Created {created} directories successfully')
