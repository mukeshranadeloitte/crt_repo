# Directory Creation Scripts

This folder contains multiple automation scripts to create the required skill directories structure.

## Directories to Create (20 total)

```
.github/
├── agents/
├── instructions/
└── skills/
    ├── sf-static-analysis/
    ├── sf-security/
    ├── sf-code-quality/
    ├── sf-architecture/
    ├── sf-data-model/
    ├── sf-governor-performance/
    ├── sf-test-quality/
    ├── sf-api-versioning/
    ├── sf-deployment/
    ├── sf-build-forms/
    ├── sf-event-driven/
    ├── sf-web-app-security/
    ├── sf-auth-session-security/
    ├── sf-shield-encryption/
    ├── sf-audit-monitoring/
    ├── sf-resilience/
    ├── sf-experience-cloud-security/
    └── sf-package-review/
```

## How to Use

### Option 1: PowerShell (Recommended for Windows 10/11)

**Prerequisites:**
- Windows PowerShell 5.1 (included with Windows 10/11)

**Steps:**
1. Open PowerShell as Administrator
2. Navigate to the repository:
   ```powershell
   cd "c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo"
   ```
3. Run the script:
   ```powershell
   .\create_skill_dirs.ps1
   ```

### Option 2: Batch File (Windows Command Prompt)

**Prerequisites:**
- Windows Command Prompt (cmd.exe) - built-in with Windows

**Steps:**
1. Open Command Prompt (cmd.exe)
2. Navigate to the repository:
   ```cmd
   cd /d "c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo"
   ```
3. Run the script:
   ```cmd
   create_all_skill_dirs.bat
   ```

### Option 3: Node.js

**Prerequisites:**
- Node.js installed

**Steps:**
1. Open Command Prompt or PowerShell
2. Navigate to the repository:
   ```
   cd "c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo"
   ```
3. Run the script:
   ```
   node create_skill_dirs.js
   ```

### Option 4: Python

**Prerequisites:**
- Python 3.6 or later installed

**Steps:**
1. Open Command Prompt or PowerShell
2. Navigate to the repository:
   ```
   cd "c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo"
   ```
3. Run the script:
   ```
   python create_skill_dirs_verify.py
   ```

### Option 5: Manual Command Line

If you prefer to create directories manually:

```cmd
cd /d "c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo"
mkdir .github\agents
mkdir .github\instructions
mkdir .github\skills\sf-static-analysis
mkdir .github\skills\sf-security
mkdir .github\skills\sf-code-quality
mkdir .github\skills\sf-architecture
mkdir .github\skills\sf-data-model
mkdir .github\skills\sf-governor-performance
mkdir .github\skills\sf-test-quality
mkdir .github\skills\sf-api-versioning
mkdir .github\skills\sf-deployment
mkdir .github\skills\sf-build-forms
mkdir .github\skills\sf-event-driven
mkdir .github\skills\sf-web-app-security
mkdir .github\skills\sf-auth-session-security
mkdir .github\skills\sf-shield-encryption
mkdir .github\skills\sf-audit-monitoring
mkdir .github\skills\sf-resilience
mkdir .github\skills\sf-experience-cloud-security
mkdir .github\skills\sf-package-review
```

## Files Included

| File | Type | Runtime | Description |
|------|------|---------|-------------|
| `create_skill_dirs.ps1` | PowerShell | PowerShell 5.1+ | Windows PowerShell script with colored output |
| `create_all_skill_dirs.bat` | Batch | Command Prompt | Windows batch file |
| `create_skill_dirs.js` | Node.js | Node.js 12+ | JavaScript automation script |
| `create_skill_dirs_verify.py` | Python | Python 3.6+ | Python automation script |
| `CREATE_DIRS_README.md` | Documentation | N/A | This file |

## Expected Output

When run successfully, each script will:
1. Create all 20 directories
2. Verify each directory exists
3. Display a summary report showing:
   - ✓ (checkmark) for successfully created/verified directories
   - ✗ (x mark) for any failures
   - Total count of verified directories

Example output:
```
Creating directories...

✓ Created: .github\agents
✓ Created: .github\instructions
✓ Created: .github\skills\sf-static-analysis
...

============================================================
Verification Report
============================================================

✓ .github\agents
✓ .github\instructions
✓ .github\skills\sf-static-analysis
...

============================================================
Summary: 20/20 directories verified
All directories created successfully!
============================================================
```

## Troubleshooting

### Issue: "Permission Denied" Error
**Solution:** Run the script or Command Prompt as Administrator

### Issue: Python/Node.js command not found
**Solution:** 
- Check if Python/Node.js is installed: `python --version` or `node --version`
- If not installed, download from:
  - Python: https://www.python.org/downloads/
  - Node.js: https://nodejs.org/

### Issue: PowerShell execution policy error
**Solution:** Temporarily enable script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
```
Then run the script again.

### Issue: Paths with special characters fail
**Solution:** Use the batch file or PowerShell script which handle paths correctly

## Verification

After running any script, you can manually verify the directories were created:

```powershell
# PowerShell
Test-Path ".github\agents"  # Should return True
Get-ChildItem ".github\" -Directory | Select-Object Name

# Command Prompt
dir .github\
```

Or simply open File Explorer and navigate to:
`c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo\.github\`

## Support

If you encounter issues:
1. Ensure you're running from the correct directory
2. Check that you have read/write permissions
3. Try running as Administrator
4. Try a different script option (Node.js, Python, or Batch)
