@echo off
REM This script creates all required directories
cd /d c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo

REM Create main directories
if not exist ".github\agents" mkdir ".github\agents"
if not exist ".github\instructions" mkdir ".github\instructions"
if not exist ".github\skills" mkdir ".github\skills"

REM Create skill subdirectories
if not exist ".github\skills\sf-static-analysis" mkdir ".github\skills\sf-static-analysis"
if not exist ".github\skills\sf-security" mkdir ".github\skills\sf-security"
if not exist ".github\skills\sf-code-quality" mkdir ".github\skills\sf-code-quality"
if not exist ".github\skills\sf-architecture" mkdir ".github\skills\sf-architecture"
if not exist ".github\skills\sf-data-model" mkdir ".github\skills\sf-data-model"
if not exist ".github\skills\sf-governor-performance" mkdir ".github\skills\sf-governor-performance"
if not exist ".github\skills\sf-test-quality" mkdir ".github\skills\sf-test-quality"
if not exist ".github\skills\sf-api-versioning" mkdir ".github\skills\sf-api-versioning"
if not exist ".github\skills\sf-deployment" mkdir ".github\skills\sf-deployment"
if not exist ".github\skills\sf-build-forms" mkdir ".github\skills\sf-build-forms"
if not exist ".github\skills\sf-event-driven" mkdir ".github\skills\sf-event-driven"
if not exist ".github\skills\sf-web-app-security" mkdir ".github\skills\sf-web-app-security"
if not exist ".github\skills\sf-auth-session-security" mkdir ".github\skills\sf-auth-session-security"
if not exist ".github\skills\sf-shield-encryption" mkdir ".github\skills\sf-shield-encryption"
if not exist ".github\skills\sf-audit-monitoring" mkdir ".github\skills\sf-audit-monitoring"
if not exist ".github\skills\sf-resilience" mkdir ".github\skills\sf-resilience"
if not exist ".github\skills\sf-experience-cloud-security" mkdir ".github\skills\sf-experience-cloud-security"
if not exist ".github\skills\sf-package-review" mkdir ".github\skills\sf-package-review"

REM Create .gitkeep files
type nul > ".github\agents\.gitkeep"
type nul > ".github\instructions\.gitkeep"
type nul > ".github\skills\sf-static-analysis\.gitkeep"
type nul > ".github\skills\sf-security\.gitkeep"
type nul > ".github\skills\sf-code-quality\.gitkeep"
type nul > ".github\skills\sf-architecture\.gitkeep"
type nul > ".github\skills\sf-data-model\.gitkeep"
type nul > ".github\skills\sf-governor-performance\.gitkeep"
type nul > ".github\skills\sf-test-quality\.gitkeep"
type nul > ".github\skills\sf-api-versioning\.gitkeep"
type nul > ".github\skills\sf-deployment\.gitkeep"
type nul > ".github\skills\sf-build-forms\.gitkeep"
type nul > ".github\skills\sf-event-driven\.gitkeep"
type nul > ".github\skills\sf-web-app-security\.gitkeep"
type nul > ".github\skills\sf-auth-session-security\.gitkeep"
type nul > ".github\skills\sf-shield-encryption\.gitkeep"
type nul > ".github\skills\sf-audit-monitoring\.gitkeep"
type nul > ".github\skills\sf-resilience\.gitkeep"
type nul > ".github\skills\sf-experience-cloud-security\.gitkeep"
type nul > ".github\skills\sf-package-review\.gitkeep"

echo All directories and .gitkeep files created!
