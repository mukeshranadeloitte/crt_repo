import os
import shutil
import sys

base_path = r'c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo'

# Create directories
agents_dir = os.path.join(base_path, '.github', 'agents')
prompts_dir = os.path.join(base_path, '.github', 'prompts')

try:
    os.makedirs(agents_dir, exist_ok=True)
    os.makedirs(prompts_dir, exist_ok=True)
    print('✓ Created directories:')
    print(f'  - {agents_dir}')
    print(f'  - {prompts_dir}')
except Exception as e:
    print(f'✗ Error creating directories: {e}')
    sys.exit(1)

# Copy files
file1_source = os.path.join(base_path, 'e2e-uat-pipeline.agent.md')
file1_dest = os.path.join(agents_dir, 'e2e-uat-pipeline.agent.md')
file2_source = os.path.join(base_path, 'create-e2e-uat-pipeline.prompt.md')
file2_dest = os.path.join(prompts_dir, 'create-e2e-uat-pipeline.prompt.md')

try:
    shutil.copy2(file1_source, file1_dest)
    shutil.copy2(file2_source, file2_dest)
    print('\n✓ Copied files:')
    print(f'  - {file1_dest}')
    print(f'  - {file2_dest}')
except Exception as e:
    print(f'✗ Error copying files: {e}')
    sys.exit(1)

# Verify files
print('\n✓ File Verification:')
if os.path.exists(file1_dest):
    size1 = os.path.getsize(file1_dest)
    print(f'  ✓ .github/agents/e2e-uat-pipeline.agent.md: {size1} bytes')
else:
    print(f'  ✗ .github/agents/e2e-uat-pipeline.agent.md NOT FOUND')

if os.path.exists(file2_dest):
    size2 = os.path.getsize(file2_dest)
    print(f'  ✓ .github/prompts/create-e2e-uat-pipeline.prompt.md: {size2} bytes')
else:
    print(f'  ✗ .github/prompts/create-e2e-uat-pipeline.prompt.md NOT FOUND')

# Show directory structure
print('\n✓ .github Directory Structure:')
github_path = os.path.join(base_path, '.github')

def show_tree(dir_path, prefix='', max_depth=3, current_depth=0):
    if current_depth >= max_depth:
        return
    try:
        items = sorted(os.listdir(dir_path))
        dirs = [item for item in items if os.path.isdir(os.path.join(dir_path, item))]
        files = [item for item in items if os.path.isfile(os.path.join(dir_path, item))]
        
        # Show directories first
        all_items = dirs + files
        for i, item in enumerate(all_items):
            full_path = os.path.join(dir_path, item)
            is_last = i == len(all_items) - 1
            connector = '└── ' if is_last else '├── '
            
            if os.path.isdir(full_path):
                print(f'{prefix}{connector}📁 {item}/')
                if item not in ['.git', '__pycache__']:
                    next_prefix = prefix + ('    ' if is_last else '│   ')
                    show_tree(full_path, next_prefix, max_depth, current_depth + 1)
            else:
                size = os.path.getsize(full_path)
                print(f'{prefix}{connector}📄 {item} ({size} bytes)')
    except Exception as e:
        print(f'{prefix}Error: {e}')

show_tree(github_path)

print('\n✓ Task completed successfully!')
