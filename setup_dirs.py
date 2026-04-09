import os
import shutil

base_path = r'c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo'

# Create directories
agents_dir = os.path.join(base_path, '.github', 'agents')
prompts_dir = os.path.join(base_path, '.github', 'prompts')

os.makedirs(agents_dir, exist_ok=True)
os.makedirs(prompts_dir, exist_ok=True)

print('✓ Created directories:')
print('  - .github/agents')
print('  - .github/prompts')

# Copy files
file1_source = os.path.join(base_path, 'e2e-uat-pipeline.agent.md')
file1_dest = os.path.join(agents_dir, 'e2e-uat-pipeline.agent.md')
file2_source = os.path.join(base_path, 'create-e2e-uat-pipeline.prompt.md')
file2_dest = os.path.join(prompts_dir, 'create-e2e-uat-pipeline.prompt.md')

shutil.copy2(file1_source, file1_dest)
shutil.copy2(file2_source, file2_dest)

print('\n✓ Copied files:')
print(f'  - {file1_dest}')
print(f'  - {file2_dest}')

# Verify files
print('\n✓ Verification:')
if os.path.exists(file1_dest):
    size1 = os.path.getsize(file1_dest)
    print(f'  File 1 (.github/agents/e2e-uat-pipeline.agent.md): FOUND ({size1} bytes)')
if os.path.exists(file2_dest):
    size2 = os.path.getsize(file2_dest)
    print(f'  File 2 (.github/prompts/create-e2e-uat-pipeline.prompt.md): FOUND ({size2} bytes)')

# Show directory structure
print('\n✓ Directory Structure:')
def show_tree(dir_path, prefix=''):
    try:
        items = sorted(os.listdir(dir_path))
        for i, item in enumerate(items):
            if item == '__pycache__':
                continue
            full_path = os.path.join(dir_path, item)
            is_last = i == len(items) - 1
            connector = '└── ' if is_last else '├── '
            print(prefix + connector + item)
            
            if os.path.isdir(full_path) and item not in ['workflows', '.git']:
                next_prefix = prefix + ('    ' if is_last else '│   ')
                show_tree(full_path, next_prefix)
    except Exception as e:
        print(f'Error reading directory: {e}')

github_path = os.path.join(base_path, '.github')
show_tree(github_path)
