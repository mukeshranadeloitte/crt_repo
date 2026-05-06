#!/usr/bin/env python3
import os
import sys

base_path = r'c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo'

directories = [
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
]

print('Creating directories...\n')

created = 0
errors = 0

for dir_path in directories:
    try:
        full_path = os.path.join(base_path, dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f'✓ Created: {dir_path}')
        created += 1
    except Exception as err:
        print(f'✗ Error creating {dir_path}: {err}')
        errors += 1

print('\n' + '='*60)
print('Verification Report')
print('='*60 + '\n')

verified = 0
for dir_path in directories:
    full_path = os.path.join(base_path, dir_path)
    exists = os.path.isdir(full_path)
    if exists:
        print(f'✓ {dir_path}')
        verified += 1
    else:
        print(f'✗ {dir_path} - NOT FOUND')

print('\n' + '='*60)
print(f'Summary: {verified}/{len(directories)} directories verified')
if errors > 0:
    print(f'Errors encountered: {errors}')
    sys.exit(1)
else:
    print('All directories created successfully!')
    sys.exit(0)
