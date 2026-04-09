---
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
