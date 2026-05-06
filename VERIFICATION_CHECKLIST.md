# Directory Creation Checklist & Verification Guide

## Pre-Execution Checklist

Before running any script, verify:

- [ ] You are in the correct directory: `c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo`
- [ ] You have Administrator privileges (if needed for your method)
- [ ] You have the required tool installed (PowerShell/Node.js/Python)
- [ ] You can see the `.github` folder already exists in this directory

## Script Execution Checklist

### If Using PowerShell Script (create_skill_dirs.ps1):
- [ ] Opened PowerShell as Administrator
- [ ] Navigated to the correct directory
- [ ] Ran: `.\create_skill_dirs.ps1`
- [ ] Script completed without errors
- [ ] Saw output showing all 20 directories verified

### If Using Batch Script (create_all_skill_dirs.bat):
- [ ] Opened Command Prompt as Administrator
- [ ] Navigated to the correct directory  
- [ ] Ran: `create_all_skill_dirs.bat`
- [ ] Script completed without errors
- [ ] Saw output showing all 20 directories verified

### If Using Node.js Script (create_skill_dirs.js):
- [ ] Opened Command Prompt or PowerShell
- [ ] Verified Node.js is installed: `node --version`
- [ ] Navigated to the correct directory
- [ ] Ran: `node create_skill_dirs.js`
- [ ] Script completed without errors
- [ ] Saw output showing all 20 directories verified

### If Using Python Script (create_skill_dirs_verify.py):
- [ ] Opened Command Prompt or PowerShell
- [ ] Verified Python is installed: `python --version`
- [ ] Navigated to the correct directory
- [ ] Ran: `python create_skill_dirs_verify.py`
- [ ] Script completed without errors
- [ ] Saw output showing all 20 directories verified

## Post-Execution Verification

### Manual Verification (File Explorer Method):
1. Open File Explorer
2. Navigate to: `c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo`
3. Double-click the `.github` folder
4. Verify you see these items:
   - [ ] `agents` (folder)
   - [ ] `instructions` (folder)
   - [ ] `skills` (folder)
   - [ ] Other existing files (workflows, JSON files, etc.)
5. Double-click `skills` folder
6. Count the folders - you should see **18 subdirectories**:
   - [ ] sf-static-analysis
   - [ ] sf-security
   - [ ] sf-code-quality
   - [ ] sf-architecture
   - [ ] sf-data-model
   - [ ] sf-governor-performance
   - [ ] sf-test-quality
   - [ ] sf-api-versioning
   - [ ] sf-deployment
   - [ ] sf-build-forms
   - [ ] sf-event-driven
   - [ ] sf-web-app-security
   - [ ] sf-auth-session-security
   - [ ] sf-shield-encryption
   - [ ] sf-audit-monitoring
   - [ ] sf-resilience
   - [ ] sf-experience-cloud-security
   - [ ] sf-package-review

### Command Line Verification (PowerShell Method):
```powershell
# Navigate to directory
cd "c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo"

# Check if agents directory exists
Test-Path ".github\agents"
# Expected: True

# Check if instructions directory exists
Test-Path ".github\instructions"
# Expected: True

# Count directories in skills
(Get-ChildItem ".github\skills" -Directory).Count
# Expected: 18

# List all skills directories
Get-ChildItem ".github\skills" -Directory | Select-Object -ExpandProperty Name
# Expected: Should list all 18 skill directory names

# Get complete structure
Get-ChildItem ".github" -Recurse -Directory | Select-Object -ExpandProperty FullName
```

### Command Line Verification (Command Prompt Method):
```cmd
REM Navigate to directory
cd /d "c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo"

REM Check if directories exist
if exist ".github\agents" (
    echo agents directory EXISTS
) else (
    echo agents directory NOT FOUND
)

if exist ".github\instructions" (
    echo instructions directory EXISTS
) else (
    echo instructions directory NOT FOUND
)

if exist ".github\skills" (
    echo skills directory EXISTS
) else (
    echo skills directory NOT FOUND
)

REM List all items in .github
dir .github

REM List all skills subdirectories
dir .github\skills

REM Get more detailed tree view
tree .github
```

## Expected Directory Tree

After successful execution, here's what the directory structure should look like:

```
c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo\.github\
│
├── agents\                          (NEW - CREATED)
│   └── (empty)
│
├── instructions\                    (NEW - CREATED)
│   └── (empty)
│
├── skills\                          (NEW - CREATED)
│   ├── sf-static-analysis\
│   ├── sf-security\
│   ├── sf-code-quality\
│   ├── sf-architecture\
│   ├── sf-data-model\
│   ├── sf-governor-performance\
│   ├── sf-test-quality\
│   ├── sf-api-versioning\
│   ├── sf-deployment\
│   ├── sf-build-forms\
│   ├── sf-event-driven\
│   ├── sf-web-app-security\
│   ├── sf-auth-session-security\
│   ├── sf-shield-encryption\
│   ├── sf-audit-monitoring\
│   ├── sf-resilience\
│   ├── sf-experience-cloud-security\
│   └── sf-package-review\
│
├── workflows\                       (EXISTING - DO NOT MODIFY)
│   ├── CRTmain.yml
│   ├── CRTEnhanceUpdate.yml
│   ├── CRTCheck.yml
│   ├── sf-scanner-waivers.csv
│   └── e2e-uat-pipeline.yml
│   └── uat-trigger-crt.yml
│
├── agents-temp-test.md             (EXISTING - DO NOT MODIFY)
├── sca-waivers.json                (EXISTING - DO NOT MODIFY)
├── sf-scanner-waivers.csv          (EXISTING - DO NOT MODIFY)
└── sf-scanner-waivers.json         (EXISTING - DO NOT MODIFY)
```

## Count Verification

| Item | Expected | Actual |
|------|----------|--------|
| Top-level new directories | 2 | ____ |
| Subdirectories under skills | 18 | ____ |
| **TOTAL NEW DIRECTORIES** | **20** | ____ |

## Success Criteria

All of the following must be true for successful completion:

- [ ] `.github\agents` directory exists and is empty
- [ ] `.github\instructions` directory exists and is empty
- [ ] `.github\skills` directory exists
- [ ] All 18 skill directories exist inside `.github\skills`
- [ ] No errors during script execution
- [ ] Script verification report shows "20/20 directories verified"

## If Something Goes Wrong

### Issue: Directories don't appear after running script

**Troubleshooting Steps:**
1. [ ] Verify you ran the command from the correct directory
2. [ ] Check File Explorer refresh (press F5)
3. [ ] Close and reopen File Explorer window
4. [ ] Try running the script again with Administrator privileges
5. [ ] Check for error messages in the script output
6. [ ] Try a different script method (switch from Batch to PowerShell, etc.)

### Issue: "Access Denied" error

**Troubleshooting Steps:**
1. [ ] Run Command Prompt/PowerShell as Administrator
2. [ ] Check that the .github folder is not locked or read-only
3. [ ] Ensure you have write permissions to the repository
4. [ ] Check antivirus isn't blocking file operations
5. [ ] Try again after a few seconds

### Issue: Some directories created but not all

**Troubleshooting Steps:**
1. [ ] Re-run the script - it will create missing ones
2. [ ] Check disk space (ensure > 1GB available)
3. [ ] Check for permission issues on specific directories
4. [ ] Manually create any missing directories:
   ```cmd
   mkdir .github\skills\[missing-directory-name]
   ```

## Final Sign-Off

Once all items are verified, you can confirm:

**✓ COMPLETED ON:** _______________

**✓ VERIFIED BY:** _______________

**✓ ALL 20 DIRECTORIES CREATED SUCCESSFULLY** ✓

---

## Additional Notes

- New directories are initially empty - this is expected
- Directories can have files/agents added later
- The directory structure is now ready for use with GitHub Copilot agents and skills
- No files need to be moved or modified

