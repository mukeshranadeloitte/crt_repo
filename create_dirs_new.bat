@echo off
cd /d "c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo"

mkdir ".github\agents"
mkdir ".github\instructions"
mkdir ".github\skills\sf-static-analysis"
mkdir ".github\skills\sf-security"
mkdir ".github\skills\sf-code-quality"
mkdir ".github\skills\sf-architecture"
mkdir ".github\skills\sf-data-model"
mkdir ".github\skills\sf-governor-performance"
mkdir ".github\skills\sf-test-quality"
mkdir ".github\skills\sf-api-versioning"
mkdir ".github\skills\sf-deployment"
mkdir ".github\skills\sf-build-forms"
mkdir ".github\skills\sf-event-driven"
mkdir ".github\skills\sf-web-app-security"
mkdir ".github\skills\sf-auth-session-security"
mkdir ".github\skills\sf-shield-encryption"
mkdir ".github\skills\sf-audit-monitoring"
mkdir ".github\skills\sf-resilience"
mkdir ".github\skills\sf-experience-cloud-security"
mkdir ".github\skills\sf-package-review"

echo.
echo Directories created. Verifying...
echo.

if exist ".github\agents" echo ✓ .github\agents
if exist ".github\instructions" echo ✓ .github\instructions
if exist ".github\skills\sf-static-analysis" echo ✓ .github\skills\sf-static-analysis
if exist ".github\skills\sf-security" echo ✓ .github\skills\sf-security
if exist ".github\skills\sf-code-quality" echo ✓ .github\skills\sf-code-quality
if exist ".github\skills\sf-architecture" echo ✓ .github\skills\sf-architecture
if exist ".github\skills\sf-data-model" echo ✓ .github\skills\sf-data-model
if exist ".github\skills\sf-governor-performance" echo ✓ .github\skills\sf-governor-performance
if exist ".github\skills\sf-test-quality" echo ✓ .github\skills\sf-test-quality
if exist ".github\skills\sf-api-versioning" echo ✓ .github\skills\sf-api-versioning
if exist ".github\skills\sf-deployment" echo ✓ .github\skills\sf-deployment
if exist ".github\skills\sf-build-forms" echo ✓ .github\skills\sf-build-forms
if exist ".github\skills\sf-event-driven" echo ✓ .github\skills\sf-event-driven
if exist ".github\skills\sf-web-app-security" echo ✓ .github\skills\sf-web-app-security
if exist ".github\skills\sf-auth-session-security" echo ✓ .github\skills\sf-auth-session-security
if exist ".github\skills\sf-shield-encryption" echo ✓ .github\skills\sf-shield-encryption
if exist ".github\skills\sf-audit-monitoring" echo ✓ .github\skills\sf-audit-monitoring
if exist ".github\skills\sf-resilience" echo ✓ .github\skills\sf-resilience
if exist ".github\skills\sf-experience-cloud-security" echo ✓ .github\skills\sf-experience-cloud-security
if exist ".github\skills\sf-package-review" echo ✓ .github\skills\sf-package-review

pause
