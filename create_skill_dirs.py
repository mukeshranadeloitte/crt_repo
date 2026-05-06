#!/usr/bin/env python3
import os
import subprocess
import sys

base_path = r"c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo"

# Define all directories to create
directories = [
    r".github\agents",
    r".github\instructions",
    r".github\skills\sf-static-analysis",
    r".github\skills\sf-security",
    r".github\skills\sf-code-quality",
    r".github\skills\sf-architecture",
    r".github\skills\sf-data-model",
    r".github\skills\sf-governor-performance",
    r".github\skills\sf-test-quality",
    r".github\skills\sf-api-versioning",
    r".github\skills\sf-deployment",
    r".github\skills\sf-build-forms",
    r".github\skills\sf-event-driven",
    r".github\skills\sf-web-app-security",
    r".github\skills\sf-auth-session-security",
    r".github\skills\sf-shield-encryption",
    r".github\skills\sf-audit-monitoring",
    r".github\skills\sf-resilience",
    r".github\skills\sf-experience-cloud-security",
    r".github\skills\sf-package-review"
]

print("Creating directories...\n")

created_count = 0
already_exist_count = 0

# Create each directory
for dir_path in directories:
    full_path = os.path.join(base_path, dir_path)
    try:
        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)
            print(f"✓ Created: {dir_path}")
            created_count += 1
        else:
            print(f"✓ Already exists: {dir_path}")
            already_exist_count += 1
    except Exception as err:
        print(f"✗ Error creating {dir_path}: {str(err)}")

print(f"\n--- Verification ---\n")
print(f"Verifying all directories exist:\n")

all_exist = True
for dir_path in directories:
    full_path = os.path.join(base_path, dir_path)
    if os.path.exists(full_path) and os.path.isdir(full_path):
        print(f"✓ {dir_path}")
    else:
        print(f"✗ {dir_path} (MISSING)")
        all_exist = False

print(f"\n--- Summary ---")
print(f"Created: {created_count}")
print(f"Already existed: {already_exist_count}")
print(f"Total: {len(directories)}")

if all_exist:
    print(f"\n✓ All {len(directories)} directories created successfully!")
    sys.exit(0)
else:
    print(f"\n✗ Some directories are missing")
    sys.exit(1)
