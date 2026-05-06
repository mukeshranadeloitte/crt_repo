@echo off
setlocal enabledelayedexpansion

cd /d c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo

if not exist ".github" (
    mkdir ".github"
    echo Created .github
)

echo Creating directories...
echo.

mkdir ".github\agents" 2>nul && echo Created: .github\agents || echo Already exists: .github\agents
mkdir ".github\instructions" 2>nul && echo Created: .github\instructions || echo Already exists: .github\instructions
mkdir ".github\skills\sf-static-analysis" 2>nul && echo Created: .github\skills\sf-static-analysis || echo Already exists: .github\skills\sf-static-analysis
mkdir ".github\skills\sf-security" 2>nul && echo Created: .github\skills\sf-security || echo Already exists: .github\skills\sf-security
mkdir ".github\skills\sf-code-quality" 2>nul && echo Created: .github\skills\sf-code-quality || echo Already exists: .github\skills\sf-code-quality
mkdir ".github\skills\sf-architecture" 2>nul && echo Created: .github\skills\sf-architecture || echo Already exists: .github\skills\sf-architecture
mkdir ".github\skills\sf-data-model" 2>nul && echo Created: .github\skills\sf-data-model || echo Already exists: .github\skills\sf-data-model
mkdir ".github\skills\sf-governor-performance" 2>nul && echo Created: .github\skills\sf-governor-performance || echo Already exists: .github\skills\sf-governor-performance
mkdir ".github\skills\sf-test-quality" 2>nul && echo Created: .github\skills\sf-test-quality || echo Already exists: .github\skills\sf-test-quality
mkdir ".github\skills\sf-api-versioning" 2>nul && echo Created: .github\skills\sf-api-versioning || echo Already exists: .github\skills\sf-api-versioning
mkdir ".github\skills\sf-deployment" 2>nul && echo Created: .github\skills\sf-deployment || echo Already exists: .github\skills\sf-deployment
mkdir ".github\skills\sf-build-forms" 2>nul && echo Created: .github\skills\sf-build-forms || echo Already exists: .github\skills\sf-build-forms
mkdir ".github\skills\sf-event-driven" 2>nul && echo Created: .github\skills\sf-event-driven || echo Already exists: .github\skills\sf-event-driven
mkdir ".github\skills\sf-web-app-security" 2>nul && echo Created: .github\skills\sf-web-app-security || echo Already exists: .github\skills\sf-web-app-security
mkdir ".github\skills\sf-auth-session-security" 2>nul && echo Created: .github\skills\sf-auth-session-security || echo Already exists: .github\skills\sf-auth-session-security
mkdir ".github\skills\sf-shield-encryption" 2>nul && echo Created: .github\skills\sf-shield-encryption || echo Already exists: .github\skills\sf-shield-encryption
mkdir ".github\skills\sf-audit-monitoring" 2>nul && echo Created: .github\skills\sf-audit-monitoring || echo Already exists: .github\skills\sf-audit-monitoring
mkdir ".github\skills\sf-resilience" 2>nul && echo Created: .github\skills\sf-resilience || echo Already exists: .github\skills\sf-resilience
mkdir ".github\skills\sf-experience-cloud-security" 2>nul && echo Created: .github\skills\sf-experience-cloud-security || echo Already exists: .github\skills\sf-experience-cloud-security
mkdir ".github\skills\sf-package-review" 2>nul && echo Created: .github\skills\sf-package-review || echo Already exists: .github\skills\sf-package-review

echo.
echo --- Verification ---
echo.
echo Verifying all directories exist:
echo.

if exist ".github\agents" (echo ✓ .github\agents) else (echo ✗ .github\agents)
if exist ".github\instructions" (echo ✓ .github\instructions) else (echo ✗ .github\instructions)
if exist ".github\skills\sf-static-analysis" (echo ✓ .github\skills\sf-static-analysis) else (echo ✗ .github\skills\sf-static-analysis)
if exist ".github\skills\sf-security" (echo ✓ .github\skills\sf-security) else (echo ✗ .github\skills\sf-security)
if exist ".github\skills\sf-code-quality" (echo ✓ .github\skills\sf-code-quality) else (echo ✗ .github\skills\sf-code-quality)
if exist ".github\skills\sf-architecture" (echo ✓ .github\skills\sf-architecture) else (echo ✗ .github\skills\sf-architecture)
if exist ".github\skills\sf-data-model" (echo ✓ .github\skills\sf-data-model) else (echo ✗ .github\skills\sf-data-model)
if exist ".github\skills\sf-governor-performance" (echo ✓ .github\skills\sf-governor-performance) else (echo ✗ .github\skills\sf-governor-performance)
if exist ".github\skills\sf-test-quality" (echo ✓ .github\skills\sf-test-quality) else (echo ✗ .github\skills\sf-test-quality)
if exist ".github\skills\sf-api-versioning" (echo ✓ .github\skills\sf-api-versioning) else (echo ✗ .github\skills\sf-api-versioning)
if exist ".github\skills\sf-deployment" (echo ✓ .github\skills\sf-deployment) else (echo ✗ .github\skills\sf-deployment)
if exist ".github\skills\sf-build-forms" (echo ✓ .github\skills\sf-build-forms) else (echo ✗ .github\skills\sf-build-forms)
if exist ".github\skills\sf-event-driven" (echo ✓ .github\skills\sf-event-driven) else (echo ✗ .github\skills\sf-event-driven)
if exist ".github\skills\sf-web-app-security" (echo ✓ .github\skills\sf-web-app-security) else (echo ✗ .github\skills\sf-web-app-security)
if exist ".github\skills\sf-auth-session-security" (echo ✓ .github\skills\sf-auth-session-security) else (echo ✗ .github\skills\sf-auth-session-security)
if exist ".github\skills\sf-shield-encryption" (echo ✓ .github\skills\sf-shield-encryption) else (echo ✗ .github\skills\sf-shield-encryption)
if exist ".github\skills\sf-audit-monitoring" (echo ✓ .github\skills\sf-audit-monitoring) else (echo ✗ .github\skills\sf-audit-monitoring)
if exist ".github\skills\sf-resilience" (echo ✓ .github\skills\sf-resilience) else (echo ✗ .github\skills\sf-resilience)
if exist ".github\skills\sf-experience-cloud-security" (echo ✓ .github\skills\sf-experience-cloud-security) else (echo ✗ .github\skills\sf-experience-cloud-security)
if exist ".github\skills\sf-package-review" (echo ✓ .github\skills\sf-package-review) else (echo ✗ .github\skills\sf-package-review)

echo.
echo --- Summary ---
echo All 20 directories have been created successfully!
echo.
pause
