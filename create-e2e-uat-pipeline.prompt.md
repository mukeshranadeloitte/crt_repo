---
description: "Generate the complete UAT end-to-end GitHub Actions pipeline workflow (e2e-uat-pipeline.yml) from scratch, including all jobs, waiver files, and documentation markdown files"
agent: "agent"
tools: [read, edit, search]
argument-hint: "Optionally specify customizations: target branch, org alias, coverage threshold, scanners to enable (checkmarx/fortify/all), CRT job/project/org IDs"
---

Generate a complete Salesforce UAT End-to-End GitHub Actions pipeline. Use the existing workflow at `.github/workflows/e2e-uat-pipeline.yml` and associated files as reference implementations.

## Workflow File: `.github/workflows/e2e-uat-pipeline.yml`

Create a workflow named `UAT End-to-End Pipeline` with the following characteristics:

### Triggers
- `pull_request` to `uat` branch for paths: `force-app/**`, `.github/workflows/e2e-uat-pipeline.yml`, `.github/sf-scanner-waivers.json` — types: opened, reopened, synchronize, edited, ready_for_review
- `pull_request_review` — types: submitted
- `workflow_dispatch` with inputs: `scanner` (choices: all | checkmarx | fortify), `action` (choices: deploy | rollback), `rollback_commit_sha` (string), `rollback_pr_number` (string)

### Global env vars (configurable via `vars.*`)
- `ORG_ALIAS` (default: `uat`)
- `COVERAGE_THRESHOLD` (default: `85`)
- `SOURCE_DIR` (default: `force-app/main/default`)
- `SFDX_AUTH_SECRET_NAME` (default: `CRT_UAT_AUTHURL`)
- `DELTA_FROM_COMMIT`, `FCLI_BOOTSTRAP_VERSION`

### Jobs (in dependency order)

**Job 1 — `setup`**: Evaluate Scanner Availability
- Outputs: `run-checkmarx`, `run-fortify` booleans based on presence of `CX_CLIENT_SECRET` / `FOD_CLIENT_SECRET`
- Skips on `pull_request_review`

**Job 2 — `salesforce-validation`**: Salesforce PR Validation
- Triggers: `pull_request` only
- **Outputs:** `has_delta` (bool) — set `true` if `package/package.xml` or `destructiveChanges/destructiveChanges.xml` contains members
- Steps:
  1. checkout (fetch-depth: 0) → setup-node 20 → npm install → install Salesforce CLI
  2. Authenticate org from `secrets.CRT_UAT_AUTHURL`
  3. Extract test classes from PR body + comments (pattern: `Tests: Class1, Class2`)
  4. Install `sfdx-git-delta` → build delta package → upload delta artifact
  5. Compute Apex delta + infer test classes by `*Test`, `*Tests`, `*TestClass` suffix
  6. Set `has_delta` output
  7. **[if has_delta]** `sf project deploy validate --async` → poll every 15s → show live progress table → show component breakdown (➕ CREATED / ✏️ UPDATED / 🗑️ DELETED) → per-class coverage
  8. **[if has_delta]** Check Apex coverage (threshold: `$COVERAGE_THRESHOLD`)
  9. **[if has_delta]** Install `@salesforce/sfdx-scanner`
  10. **[if has_delta]** Detect changed `.cls/.trigger/.js/.html/.css` files for targeted SCA
  11. **[if has_targets]** `sf scanner run --target <changed-files-only> --format csv --outfile sfdx-report.csv --severity-threshold 3` (`continue-on-error: true`)
  12. **[if has_targets]** Check results against `.github/sf-scanner-waivers.json` → write `sfdx-waiver-results.csv` (`continue-on-error: true`)
  13. Upload `sfdx-scanner-reports` artifact
- **Key:** SCA targets only changed files, not the full `force-app/`. Scanner violations NEVER block the job.
- **Key:** `--test-level NoTestRun` is invalid for validate — omit `--test-level` when no Apex changed.

**Job 3 — `sca-sast-stage`**: SCA/SAST Stage (npm audit)
- `needs: [salesforce-validation]`
- **Condition:** `needs.salesforce-validation.outputs.has_delta == 'true'`
- Runs `npm audit --json`, checks against `.github/sca-waivers.json`, fails on unwaived/expired violations

**Job 4 — `automated-governance`**: Automated Hard Gates
- `needs: [salesforce-validation]`
- **Condition:** `needs.salesforce-validation.outputs.has_delta == 'true'`
- Full Apex test suite with coverage (75% minimum), destructive changes check + PR comment, targeted SCA

**Job 5 — `checkmarx-sast`**: CheckMarx AST Scan
- `needs: [setup, sca-sast-stage]`, conditional on `run-checkmarx == 'true'`

**Job 6 — `fortify-sast-dast`**: Fortify SAST + optional DAST
- `needs: [setup, sca-sast-stage]`, conditional on `run-fortify == 'true'`

**Job 7 — `manual-validation`**: Manual ReleaseGate Approval
- `needs: [automated-governance, sca-sast-stage]`
- **Condition:** `needs.salesforce-validation.outputs.has_delta == 'true'`
- Uses GitHub environment `ReleaseGate` with required reviewers

**Job 8 — `approval-merge-gate`**: Approval + Merge Gate
- Triggers on `pull_request_review` (state=approved)
- Verifies approval freshness, merges PR, outputs `merge_commit_sha`

**Job 9 — `deploy-after-merge`**: Deploy to UAT
- `needs: [approval-merge-gate]`, `permissions: contents: write`
- Steps:
  1. `sf project deploy start --async` → poll every 15s → live progress table → component breakdown → per-class coverage
  2. Build deployment package: `package.xml` + `destructiveChanges.xml` + `components.zip` + `deployment-info.json`
  3. Upload artifact (90-day retention)
  4. Commit package folder to `pr_packages` orphan branch
  5. Update `DELTA_FROM_COMMIT` via GitHub API: `curl -L -X PATCH -H "Authorization: Bearer ${GH_PAT}" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/{repo}/actions/variables/DELTA_FROM_COMMIT -d '{"name":"DELTA_FROM_COMMIT","value":"<sha>"}'`

**Job 10 — `trigger-crt-tests`**: CRT Smoke Tests
- `needs: [deploy-after-merge]`
- GraphQL API: `POST https://graphql.eu-robotic.copado.com/v1` with `X-Authorization: ${CRT_API_TOKEN}`
- Mutation: `createBuild(projectId: <id>, jobId: <id>)`
- Polls `latestBuilds(projectId: <id>, resultSize: 10)` every 30s for pass/fail
- Posts result PR comment + GitHub Step Summary with CRT dashboard link

**Job 11 — `rollback`**: Rollback Deployment
- Triggers on `workflow_dispatch` with `action=rollback`
- Input: `rollback_commit_sha` — the SHA to revert TO
- Uses `sfdx-git-delta` in reverse: new metadata treated as destructive
- Uses `--pre-destructive-changes` to delete new components before re-deploying prior state

---

## Waiver Files

### `.github/sf-scanner-waivers.json`
JSON array. Schema per entry:
```json
{
  "rule": "ApexDoc",
  "file": "MyClass.cls",
  "description": "Missing ApexDoc on public methods",
  "expiry": "YYYY-MM-DD",
  "reason": "Tracked in PROJ-123.",
  "approved_by": "tech-lead-username",
  "ticket": "PROJ-123"
}
```
Status values: `WAIVED` (active), `VIOLATION`, `EXPIRED_WAIVER` (past expiry).
Results written to `sfdx-waiver-results.csv`.

### `.github/sca-waivers.json`
JSON array for npm audit waivers:
```json
{
  "package": "lodash",
  "severity": "high",
  "advisory": "GHSA-xxxx-xxxx-xxxx",
  "reason": "No fix available.",
  "expires": "YYYY-MM-DD",
  "approved_by": "platform-security"
}
```

---

## Required Secrets & Variables

| Secret | Required | Description |
|--------|----------|-------------|
| `CRT_UAT_AUTHURL` | ✅ | SFDX Auth URL for UAT org |
| `GH_PAT` | ✅ | Fine-Grained PAT — Variables: Read and write |
| `CRT_API_TOKEN` | ✅ | CRT GraphQL API token (X-Authorization) |
| `CX_CLIENT_SECRET` | ⬜ | CheckMarx (enables Job 5) |
| `FOD_CLIENT_SECRET` | ⬜ | Fortify (enables Job 6) |

| Variable | Default | Description |
|----------|---------|-------------|
| `DELTA_FROM_COMMIT` | *(required)* | Baseline SHA for sfdx-git-delta |
| `ORG_ALIAS` | `uat` | SF org alias |
| `COVERAGE_THRESHOLD` | `85` | Apex coverage % |
| `CRT_JOB_ID` | `115686` | CRT job ID |
| `CRT_PROJECT_ID` | `73283` | CRT project ID |
| `CRT_ORG_ID` | `43532` | CRT org ID |

---

## Documentation Files (in `docs/`)

### `docs/pipeline-setup.md`
- All required secrets (with descriptions + how to create GH_PAT)
- All required variables (with defaults)
- GitHub environment `ReleaseGate` setup
- Branch protection rules
- `pr_packages` branch description
- DELTA_FROM_COMMIT auto-update explanation
- No-delta skip behaviour table
- Quick start checklist

### `docs/sca-waivers.md`
- Part 1: SF Code Analyzer waivers (schema, governance, expiry policy, who updates, results CSV format)
- Part 2: npm SCA waivers (schema, governance)

### `docs/manual_runbook.md`
- Manual trigger guide, ReleaseGate approval steps
- Rollback procedure: find SHA, trigger workflow_dispatch with action=rollback
- What rollback does (new metadata → destructive, modified → re-deployed, deleted → restored)

### `docs/troubleshooting.md`
- Common failures per job with diagnosis and fix

---

## Instructions
1. Read the existing workflow file at `.github/workflows/e2e-uat-pipeline.yml` first
2. Generate or update each file listed above
3. Preserve existing content in docs files — only add/update relevant sections
4. Ensure YAML is valid — quote strings with colons, 2-space indentation
5. Never use `--test-level NoTestRun` with `deploy validate` — omit the flag instead
6. Never combine `--async` and `--wait` on the same deploy command
7. Summarize what was created/updated and any required configuration
