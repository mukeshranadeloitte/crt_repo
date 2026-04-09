@echo off
REM Setup script for agent files
cd /d c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo

REM Create directories
echo Creating directories...
if not exist ".github\agents" mkdir ".github\agents"
if not exist ".github\prompts" mkdir ".github\prompts"
echo ✓ Directories created

REM Copy files
echo.
echo Copying files...
copy /Y "e2e-uat-pipeline.agent.md" ".github\agents\e2e-uat-pipeline.agent.md" >nul
copy /Y "create-e2e-uat-pipeline.prompt.md" ".github\prompts\create-e2e-uat-pipeline.prompt.md" >nul
echo ✓ Files copied

REM Verify files exist and show sizes
echo.
echo Verifying destination files:
for %%F in (".github\agents\e2e-uat-pipeline.agent.md") do (
  echo %%F - %%~zF bytes
)
for %%F in (".github\prompts\create-e2e-uat-pipeline.prompt.md") do (
  echo %%F - %%~zF bytes
)

REM Show directory structure
echo.
echo .github directory structure:
tree ".github" /A
