# PowerShell script to create skill directories
# This script is compatible with Windows PowerShell 5.1 (included with Windows 10/11)
# Run from: PowerShell as Administrator

$basePath = "c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo"
$directories = @(
    '.github\agents',
    '.github\instructions',
    '.github\skills\sf-static-analysis',
    '.github\skills\sf-security',
    '.github\skills\sf-code-quality',
    '.github\skills\sf-architecture',
    '.github\skills\sf-data-model',
    '.github\skills\sf-governor-performance',
    '.github\skills\sf-test-quality',
    '.github\skills\sf-api-versioning',
    '.github\skills\sf-deployment',
    '.github\skills\sf-build-forms',
    '.github\skills\sf-event-driven',
    '.github\skills\sf-web-app-security',
    '.github\skills\sf-auth-session-security',
    '.github\skills\sf-shield-encryption',
    '.github\skills\sf-audit-monitoring',
    '.github\skills\sf-resilience',
    '.github\skills\sf-experience-cloud-security',
    '.github\skills\sf-package-review'
)

Write-Host "Creating directories..." -ForegroundColor Cyan
Write-Host ""

$created = 0
$errors = 0

foreach ($dir in $directories) {
    try {
        $fullPath = Join-Path $basePath $dir
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
            Write-Host "✓ Created: $dir" -ForegroundColor Green
            $created++
        } else {
            Write-Host "→ Already exists: $dir" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "✗ Error creating $dir : $_" -ForegroundColor Red
        $errors++
    }
}

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "Verification Report" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""

$verified = 0
foreach ($dir in $directories) {
    $fullPath = Join-Path $basePath $dir
    if (Test-Path $fullPath -PathType Container) {
        Write-Host "✓ $dir" -ForegroundColor Green
        $verified++
    } else {
        Write-Host "✗ $dir - NOT FOUND" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host ("=" * 60)
Write-Host "Summary: $verified/$($directories.Count) directories verified"
if ($errors -gt 0) {
    Write-Host "Errors encountered: $errors" -ForegroundColor Red
} else {
    Write-Host "All directories created successfully!" -ForegroundColor Green
}
Write-Host ("=" * 60)
