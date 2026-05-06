@echo off
REM Script to create all required skill directories
REM Run from: c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo

cd /d "c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo" || exit /b 1

echo Creating directories...
echo.

REM Create all directories
mkdir ".github\agents" 2>nul
mkdir ".github\instructions" 2>nul
mkdir ".github\skills\sf-static-analysis" 2>nul
mkdir ".github\skills\sf-security" 2>nul
mkdir ".github\skills\sf-code-quality" 2>nul
mkdir ".github\skills\sf-architecture" 2>nul
mkdir ".github\skills\sf-data-model" 2>nul
mkdir ".github\skills\sf-governor-performance" 2>nul
mkdir ".github\skills\sf-test-quality" 2>nul
mkdir ".github\skills\sf-api-versioning" 2>nul
mkdir ".github\skills\sf-deployment" 2>nul
mkdir ".github\skills\sf-build-forms" 2>nul
mkdir ".github\skills\sf-event-driven" 2>nul
mkdir ".github\skills\sf-web-app-security" 2>nul
mkdir ".github\skills\sf-auth-session-security" 2>nul
mkdir ".github\skills\sf-shield-encryption" 2>nul
mkdir ".github\skills\sf-audit-monitoring" 2>nul
mkdir ".github\skills\sf-resilience" 2>nul
mkdir ".github\skills\sf-experience-cloud-security" 2>nul
mkdir ".github\skills\sf-package-review" 2>nul

echo.
echo ============================================================
echo Verification Report
echo ============================================================
echo.

REM Verify each directory
setlocal enabledelayedexpansion
set "count=0"

for %%d in (
    ".github\agents"
    ".github\instructions"
    ".github\skills\sf-static-analysis"
    ".github\skills\sf-security"
    ".github\skills\sf-code-quality"
    ".github\skills\sf-architecture"
    ".github\skills\sf-data-model"
    ".github\skills\sf-governor-performance"
    ".github\skills\sf-test-quality"
    ".github\skills\sf-api-versioning"
    ".github\skills\sf-deployment"
    ".github\skills\sf-build-forms"
    ".github\skills\sf-event-driven"
    ".github\skills\sf-web-app-security"
    ".github\skills\sf-auth-session-security"
    ".github\skills\sf-shield-encryption"
    ".github\skills\sf-audit-monitoring"
    ".github\skills\sf-resilience"
    ".github\skills\sf-experience-cloud-security"
    ".github\skills\sf-package-review"
) do (
    if exist "%%d\" (
        echo ✓ %%d
        set /a count+=1
    ) else (
        echo ✗ %%d - NOT FOUND
    )
)

echo.
echo ============================================================
echo Summary: !count!/20 directories verified
echo ============================================================
echo.

if !count! equ 20 (
    echo All directories created successfully!
    exit /b 0
) else (
    echo Some directories could not be verified.
    exit /b 1
)
