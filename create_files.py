import os
import sys

# File 1
file1_path = r'c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo\.github\agents\e2e-uat-pipeline.agent.md'
file1_content = """---
description: "Use when: working with e2e-uat-pipeline.yml, modifying or debugging the UAT end-to-end GitHub Actions workflow, adding jobs to the pipeline, understanding job dependencies, configuring Salesforce PR validation, SCA scanner waivers, CheckMarx, Fortify, CRT testing, or any Salesforce CI/CD pipeline task"
tools: [read, edit, search]
name: "E2E UAT Pipeline"
argument-hint: "Describe what you want to do with the pipeline (e.g. add a job, debug a failure, update scanner config)"
---
You are a specialist in the UAT End-to-End GitHub Actions pipeline defined in `.github/workflows/e2e-uat-pipeline.yml`. Your job is to help users understand, debug, extend, and maintain this pipeline and its associated documentation and configuration files.

## Pipeline Architecture

The pipeline has these jobs, running in order:

| # | Job ID | Name | Trigger | Depends On |
|---|--------|------|---------|------------|
| 1 | `setup` | Evaluate Scanner Availability | push/dispatch | — |
| 2 | `salesforce-validation` | Salesforce PR validation | pull_request | — |
| 3 | `sca-sast-stage` | SCA/SAST Stage (npm audit) | PR/dispatch | `salesforce-validation` |
| 4 | `automated-governance` | Automated Hard Gates | pull_request | `salesforce-validation` |
| 5 | `checkmarx-sast` | CheckMarx AST Scan | PR/dispatch | `setup`, `sca-sast-stage` |
| 6 | `fortify-sast` | Fortify SAST Scan | PR/dispatch | `setup`, `sca-sast-stage` |
| 7 | `crt-testing` | CRT Automated Testing | PR review | `salesforce-validation` |
| 8 | `deployment-gate` | Deployment Gate | PR review | all jobs |
| 9 | `deploy` | Deploy to UAT | PR review | `deployment-gate` |

## Key Files

- **Workflow**: `.github/workflows/e2e-uat-pipeline.yml`
- **SF Scanner waivers**: `.github/sf-scanner-waivers.json` (rule-based, per file, with expiry dates)
- **npm SCA waivers**: `.github/sca-waivers.json` (package-based, with expiry dates)
- **Docs**: `docs/pipeline-overview.md`, `docs/pipeline-setup.md`, `docs/sca-waivers.md`, `docs/troubleshooting.md`, `docs/manual_runbook.md`

## Waiver Systems

**Salesforce Code Analyzer waivers** (`.github/sf-scanner-waivers.json`):
- Schema: `rule`, `file`, `description`, `expiry` (YYYY-MM-DD), `reason`
- Matched by: `rule` substring in scanner Rule column AND `file` substring in file path
- Behaviour: active waiver → logged as WAIVED and skipped; expired waiver → fail with message; no waiver → logged as VIOLATION but job continues (`continue-on-error: true`)

**npm SCA waivers** (`.github/sca-waivers.json`):
- Schema: `package`, `severity`, `advisory`, `reason`, `expires` (YYYY-MM-DD), `approved_by`
- Matched by exact package name

## Constraints
- DO NOT modify deployment jobs (`deploy`, `deployment-gate`) without understanding approval gate logic
- DO NOT remove `continue-on-error: true` from scanner/waiver-check steps — violations must not block the PR validation job
- ONLY recommend changes that maintain backward compatibility with existing secrets/vars
- Always keep `needs:` dependencies consistent when adding new jobs

## Approach
1. **Read** the current workflow file before suggesting any changes
2. **Identify** which job section is relevant to the request
3. **Check** waiver files if the request involves scanner violations
4. **Edit** with minimal surgical changes — preserve existing structure and comments
5. **Update** the relevant docs in `docs/` if the change affects setup, configuration, or troubleshooting

## Output Format
For workflow changes: show the exact YAML diff or edited section with context.
For waiver additions: show the JSON entry to add to the appropriate waiver file.
For debugging: identify the failing step, its job, and the most likely root cause with a fix.
"""

# File 2
file2_path = r'c:\Users\mukerana\Documents\VS_Code\github_repo\crt_repo\.github\prompts\create-e2e-uat-pipeline.prompt.md'
file2_content = """---
description: "Generate the complete UAT end-to-end GitHub Actions pipeline workflow (e2e-uat-pipeline.yml) from scratch, including all jobs, waiver files, and documentation markdown files"
agent: "agent"
tools: [read, edit, search]
argument-hint: "Optionally specify customizations: org alias, coverage threshold, scanners to enable (checkmarx/fortify/all), CRT job/project/org IDs"
---

Generate a complete Salesforce UAT End-to-End GitHub Actions pipeline. Use the existing workflow at `.github/workflows/e2e-uat-pipeline.yml` and `.github/sf-scanner-waivers.json` as reference implementations.

## Workflow File: `.github/workflows/e2e-uat-pipeline.yml`

Create a workflow named `UAT End-to-End Pipeline` with the following characteristics:

### Triggers
- `pull_request` to `uat` branch for paths `force-app/**` — types: opened, reopened, synchronize, edited, ready_for_review
- `pull_request_review` — types: submitted
- `workflow_dispatch` with a `scanner` input (choices: all | checkmarx | fortify)

### Global env vars (configurable via `vars.*`)
- `ORG_ALIAS` (default: `uat`)
- `COVERAGE_THRESHOLD` (default: `85`)
- `SOURCE_DIR` (default: `force-app/main/default`)
- `SFDX_AUTH_SECRET_NAME`, `DELTA_FROM_COMMIT`, `FCLI_BOOTSTRAP_VERSION`

### Jobs (in dependency order)

**Job 1 — `setup`**: Evaluate Scanner Availability
- Outputs: `run-checkmarx`, `run-fortify` booleans based on presence of `CX_CLIENT_SECRET` / `FOD_CLIENT_SECRET`
- Skips on `pull_request_review`

**Job 2 — `salesforce-validation`**: Salesforce PR Validation
- Triggers: `pull_request` only
- Steps: checkout → setup-node → npm install → install Salesforce CLI → authenticate org → extract test classes from PR → install sfdx-git-delta → build delta package → compute Apex delta → validate test requirements → validate deploy (check-only) → check Apex coverage → install SF Code Analyzer → run SF Code Analyzer (`continue-on-error: true`) → check results against SF scanner waivers (`continue-on-error: true`) → upload sfdx-report
- SF scanner: `sf scanner run --target "./force-app" --format "csv" --outfile "sfdx-report.csv" --severity-threshold 3`
- Waiver check: Python inline script reads `.github/sf-scanner-waivers.json`, logs WAIVED/VIOLATION, does NOT fail the job

**Job 3 — `sca-sast-stage`**: SCA/SAST Stage
- `needs: [salesforce-validation]`
- Runs `npm audit --json --audit-level=high`, checks against `.github/sca-waivers.json`, fails on unwaived/expired violations

**Job 4 — `automated-governance`**: Automated Hard Gates
- `needs: [salesforce-validation]`
- Full Apex test suite with coverage, enforces 75% minimum, checks destructive changes, posts PR comment

**Job 5 — `checkmarx-sast`**: CheckMarx AST Scan
- `needs: [setup, sca-sast-stage]`, conditional on `run-checkmarx == 'true'`

**Job 6 — `fortify-sast`**: Fortify SAST Scan
- `needs: [setup, sca-sast-stage]`, conditional on `run-fortify == 'true'`

**Job 7 — `crt-testing`**: CRT Automated Testing
- `needs: [salesforce-validation]`, triggers on `pull_request_review`

**Job 8 — `deployment-gate`**: Deployment Gate
- `needs` all jobs, validates approvals, posts summary PR comment

**Job 9 — `deploy`**: Deploy to UAT
- `needs: [deployment-gate]`, actual deploy + destructive changes + PR comment

---

## Waiver Files

### `.github/sf-scanner-waivers.json`
JSON array for Salesforce Code Analyzer rule waivers. Schema per entry:
```json
{
  "rule": "<RuleName>",
  "file": "<filename.cls>",
  "description": "<human-readable description>",
  "expiry": "YYYY-MM-DD",
  "reason": "<justification>"
}
```

### `.github/sca-waivers.json`
JSON array for npm audit waivers. Schema per entry:
```json
{
  "package": "<pkg-name>",
  "severity": "high|critical",
  "advisory": "GHSA-xxxx-xxxx-xxxx",
  "reason": "<justification>",
  "expires": "YYYY-MM-DD",
  "approved_by": "<team>"
}
```

---

## Documentation Files (in `docs/`)

### `docs/pipeline-overview.md`
- Pipeline name, purpose, triggers, job dependency diagram, job summaries

### `docs/pipeline-setup.md`
- Prerequisites, required secrets table, required variables table, how to set SFDX auth URL, branch protection recommendations

### `docs/sca-waivers.md`
- Waiver usage guide, schema reference for both waiver files, examples, waiver lifecycle

### `docs/troubleshooting.md`
- Common failures per job with diagnosis and fix steps

### `docs/manual_runbook.md`
- Manual trigger guide, scanner bypass, rollback, emergency deployment procedures

---

## Instructions
1. Read the existing workflow file at `.github/workflows/e2e-uat-pipeline.yml` first
2. Generate or update each file listed above
3. Preserve existing content in docs files — only add/update relevant sections
4. Ensure YAML is valid — quote strings with colons, use 2-space indentation
5. Summarize what was created/updated and any required configuration
"""

def create_file_with_dirs(filepath, content):
    """Create file and parent directories if they don't exist."""
    dirpath = os.path.dirname(filepath)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)
        print(f"✓ Created directory: {dirpath}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created file: {filepath}")
    print(f"  Size: {len(content)} bytes")

try:
    create_file_with_dirs(file1_path, file1_content)
    create_file_with_dirs(file2_path, file2_content)
    print('\n✓ SUCCESS: Both files created successfully!')
except Exception as err:
    print(f'✗ ERROR: {err}', file=sys.stderr)
    sys.exit(1)
