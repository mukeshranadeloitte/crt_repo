@echo off
REM Create directories
if not exist ".github\agents" (
  mkdir ".github\agents"
  echo Created .github\agents
)

if not exist ".github\prompts" (
  mkdir ".github\prompts"
  echo Created .github\prompts
)

REM Copy files
xcopy /Y "e2e-uat-pipeline.agent.md" ".github\agents\e2e-uat-pipeline.agent.md*"
if exist ".github\agents\e2e-uat-pipeline.agent.md" (
  echo File 1 copied successfully: .github\agents\e2e-uat-pipeline.agent.md
)

xcopy /Y "create-e2e-uat-pipeline.prompt.md" ".github\prompts\create-e2e-uat-pipeline.prompt.md*"
if exist ".github\prompts\create-e2e-uat-pipeline.prompt.md" (
  echo File 2 copied successfully: .github\prompts\create-e2e-uat-pipeline.prompt.md
)

echo.
echo Verification complete!
echo Directory listing:
dir ".github\agents"
echo.
dir ".github\prompts"
