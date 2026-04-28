# UAT Pipeline — Setup & Configuration

Complete reference for all secrets, variables, tool requirements, and branch configuration for `.github/workflows/e2e-uat-pipeline.yml`.

---

## 0. Software & Tool Prerequisites

These tools are **installed automatically by the workflow** on the GitHub-hosted runner. No local installation is required for the CI/CD pipeline itself. However, developers working locally or teams setting up a new project need the following.

### Required on GitHub Actions runner (auto-installed by workflow)
| Tool | Version / Notes |
|------|----------------|
| `@salesforce/cli` (`sf`) | Latest — installed via `npm install -g @salesforce/cli` |
| `sfdx-git-delta` | Latest — installed via `echo y \| sf plugins install sfdx-git-delta` |
| `@salesforce/plugin-scanner` | Latest — installed via `sf plugins install @salesforce/plugin-scanner` |
| `jq` | Pre-installed on `ubuntu-latest` |
| `python3` | Pre-installed on `ubuntu-latest` |
| `curl` | Pre-installed on `ubuntu-latest` |
| `node` / `npm` | Pre-installed on `ubuntu-latest` (LTS) |

### Required for local development
| Tool | Install Command | Purpose |
|------|----------------|---------|
| Salesforce CLI (`sf`) | `npm install -g @salesforce/cli` | Deploy, auth, run commands locally |
| Node.js ≥ 18 | [nodejs.org](https://nodejs.org) | npm packages, ESLint, Prettier |
| Java 11+ | Required by CheckMarx CxConsole | Only needed if running CheckMarx locally |
| Git | ≥ 2.30 | `sfdx-git-delta` needs proper git history |
| `jq` | `brew install jq` / `apt install jq` | Local script testing |

### GitHub Actions runner environment
The workflow uses `ubuntu-latest` throughout. No self-hosted runners are required.

---

## 1. GitHub Repository Secrets

Set these under **Settings → Secrets and variables → Actions → Secrets**.

### Salesforce

| Secret | Required | Description |
|--------|----------|-------------|
| `CRT_UAT_AUTHURL` | ✅ Yes | SFDX auth URL for the UAT org. Generate with: `sf org display --target-org <alias> --verbose` and copy the `Sfdx Auth Url` field. |

### CheckMarx AST

> Only needed if running CheckMarx scans. If absent, the `checkmarx-sast` job is skipped.

| Secret | Required | Description |
|--------|----------|-------------|
| `CX_BASE_URI` | ✅ | CheckMarx AST server base URL (e.g. `https://ast.checkmarx.net`) |
| `CX_TENANT` | ✅ | CheckMarx tenant name |
| `CX_CLIENT_ID` | ✅ | OAuth client ID |
| `CX_CLIENT_SECRET` | ✅ | OAuth client secret (presence of this secret enables the job) |
| `CX_PROJECT_NAME` | ⬜ Optional | Project name in CheckMarx; defaults to repository name |

### Fortify on Demand

> Only needed if running Fortify scans. If absent, the `fortify-sast-dast` job is skipped.

| Secret | Required | Description |
|--------|----------|-------------|
| `FOD_CLIENT_ID` | ✅ | FoD OAuth client ID |
| `FOD_CLIENT_SECRET` | ✅ | FoD OAuth client secret (presence of this secret enables the job) |
| `FOD_APP_NAME` | ✅ | Application name in Fortify FoD |
| `FOD_RELEASE_NAME` | ✅ | Release name in Fortify FoD |
| `FOD_DAST_SCAN_URL` | ⬜ Optional | Target URL for DAST scan. If absent, DAST steps are skipped. |

### Copado Robotic Testing (CRT)

| Secret | Required | Description |
|--------|----------|-------------|
| `CRT_PAT` | ⬜ Legacy | Old PAT — replaced by `CRT_API_TOKEN` |
| `CRT_API_TOKEN` | ✅ | API token for `X-Authorization` header on the CRT GraphQL API |

### Deployment Automation

| Secret | Required | Description |
|--------|----------|-------------|
| `GH_PAT` | ✅ Recommended | Fine-Grained PAT with **Variables: Read and write** permission. Used to auto-update `DELTA_FROM_COMMIT` after each deploy. Without this, the variable must be updated manually. |

**How to create `GH_PAT`:**
1. Go to GitHub → **Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Click **Generate new token**
3. Set expiry and select this repository
4. Under **Repository permissions** → **Variables** → set to **Read and write**
5. Copy the token and save it as secret `GH_PAT` in this repository

---

## 2. GitHub Repository Variables

Set these under **Settings → Secrets and variables → Actions → Variables**.

### Salesforce

| Variable | Default | Description |
|----------|---------|-------------|
| `ORG_ALIAS` | `uat` | Alias used when authenticating to the target SF org |
| `SFDX_AUTH_SECRET_NAME` | `CRT_UAT_AUTHURL` | Name of the repository secret that holds the SFDX auth URL. Change this if you store the auth URL under a different secret name. |
| `DELTA_FROM_COMMIT` | *(none — required)* | Baseline commit SHA for `sfdx-git-delta`. **Auto-updated** after each successful deployment via `GH_PAT`. Set manually on first use. Used as a shallow-clone fallback in the deploy job (primary FROM is `git rev-parse HEAD^1`). |
| `COVERAGE_THRESHOLD` | `85` | Minimum Apex coverage % enforced by the workflow coverage check |
| `SOURCE_DIR` | `force-app/main/default` | Source directory passed to `sf scanner run` and fallback deploy |
| `SCA_ENFORCEMENT_MODE` | `enforce` | Controls how Salesforce Code Analyzer violations are handled: `enforce` (default) = expired waivers fail the pipeline; `warn` = all violations and expired waivers are warnings only (nothing fails); `off` = all SCA scanner steps are skipped entirely. **Set to `off` during initial project phase** to bypass all violations while getting the pipeline running. |

### Fortify on Demand

| Variable | Default | Description |
|----------|---------|-------------|
| `FOD_URL` | *(none)* | Fortify FoD instance URL (e.g. `https://ams.fortify.com`) |
| `FOD_DAST_ASSESSMENT_TYPE` | `Dynamic Assessment` | FoD DAST assessment type |
| `FOD_DAST_FREQUENCY` | `SingleScan` | FoD DAST scan frequency |
| `FOD_DAST_ENVIRONMENT` | `External` | FoD DAST environment type |

### Copado Robotic Testing (CRT)

| Variable | Default | Description |
|----------|---------|-------------|
| `CRT_JOB_ID` | `115686` | CRT Job ID to trigger (from the job URL) |
| `CRT_PROJECT_ID` | `73283` | CRT Project ID (from the job URL `?projectId=...`) |
| `CRT_ORG_ID` | `43532` | CRT Org ID (from the job URL `&orgId=...`) |

---

## 3. Branch Protection Rules

For the merge gate to work correctly, configure branch protection on `uat`:

1. Go to **Settings → Branches → Add rule** for branch `uat`
2. Enable **Require status checks to pass before merging**
3. Add the following as required checks:
   - `Salesforce PR validation`
   - `SCA/SAST Stage`
   - `Automated Hard Gates`
   - `CheckMarx AST Scan` *(if using CheckMarx)*
   - `Fortify on Demand Scan` *(if using Fortify)*
4. Enable **Require pull request reviews before merging** (at least 1 approval)
5. Enable **Dismiss stale pull request approvals when new commits are pushed**
6. Enable **Require branches to be up to date before merging**

---

## 4. `pr_packages` Branch — Deployment Package History

After every successful deployment, the pipeline automatically commits a deployment package to the `pr_packages` branch. This branch serves as a permanent audit log of everything deployed.

**Branch location:** `pr_packages` (created automatically on first deploy)

**Each commit contains:**

| File | Content |
|------|---------|
| `package.xml` | Salesforce components that were deployed |
| `destructiveChanges.xml` | Components that were deleted (if any) |
| `deployment-info.json` | PR number, commit SHA, timestamps, actor, run URL |

**Package naming:** `deploy-pr<PR>-<sha>-<timestamp>`

Example:
```
pr_packages/
  deploy-pr42-a1b2c3d4e5-20260409T143000Z/
    package.xml
    destructiveChanges.xml
    deployment-info.json
```

**Browse deployment history:**
```bash
git fetch origin pr_packages
git log origin/pr_packages --oneline
git show origin/pr_packages -- deploy-pr42-a1b2c3d4e5-20260409T143000Z/deployment-info.json
```

---

## 5. DELTA_FROM_COMMIT — Automatic Update

After every successful deployment, the pipeline **automatically updates** `DELTA_FROM_COMMIT` to the deployed commit SHA using the GitHub API via `GH_PAT`.

The deploy job (`deploy-after-merge`) computes its delta FROM using `git rev-parse HEAD^1` — the UAT branch tip immediately before the PR merged. This always matches what was validated in the PR, regardless of what `DELTA_FROM_COMMIT` holds. `DELTA_FROM_COMMIT` is used as a fallback only if `HEAD^1` is unavailable (shallow clone) and is still updated after deploy for rollback reference.

**If `GH_PAT` is not set:**
- The step will print a warning with the correct SHA
- You must update `DELTA_FROM_COMMIT` manually in **Settings → Variables**
- The SHA is also recorded in the `pr_packages` branch commit and `deployment-info.json`

---

## 6. Quick Start Checklist

```
SECRETS
[ ] Secret CRT_UAT_AUTHURL set to valid SFDX auth URL
[ ] Secret CRT_API_TOKEN set for CRT GraphQL API (X-Authorization header)
[ ] Secret GH_PAT set (Fine-Grained PAT, Variables: Read and write)
[ ] (Optional) CheckMarx: CX_BASE_URI, CX_TENANT, CX_CLIENT_ID, CX_CLIENT_SECRET
[ ] (Optional) CheckMarx: CX_PROJECT_NAME (defaults to repo name)
[ ] (Optional) Fortify: FOD_CLIENT_ID, FOD_CLIENT_SECRET, FOD_APP_NAME, FOD_RELEASE_NAME
[ ] (Optional) Fortify DAST: FOD_DAST_SCAN_URL

VARIABLES
[ ] Variable DELTA_FROM_COMMIT set to baseline commit SHA (first deploy only)
[ ] Variable ORG_ALIAS set (default: uat)
[ ] Variable SFDX_AUTH_SECRET_NAME set if auth URL secret uses a non-default name (default: CRT_UAT_AUTHURL)
[ ] Variable COVERAGE_THRESHOLD set (default: 85)
[ ] Variable SCA_ENFORCEMENT_MODE set (default: enforce; use off for initial project phase)
[ ] (Optional) Fortify variables: FOD_URL, FOD_DAST_ASSESSMENT_TYPE, FOD_DAST_FREQUENCY, FOD_DAST_ENVIRONMENT
[ ] (Optional) CRT variables: CRT_JOB_ID, CRT_PROJECT_ID, CRT_ORG_ID

BRANCH & REPO CONFIG
[ ] Branch protection configured on uat branch (see Section 3)
[ ] SF scanner waiver file: .github/sf-scanner-waivers.csv committed to main branch
[ ] pr_packages branch — created automatically on first deploy (no action needed)
```

---

## 7. No-Delta Behaviour (skip logic)

When a PR contains no Salesforce component changes (e.g. only workflow YAML or docs changed), the pipeline **automatically skips** expensive steps:

| What is skipped | Condition |
|---|---|
| Deploy validation (`sf project deploy validate`) | `has_delta == false` |
| Apex coverage check | `has_delta == false` |
| SF Code Analyzer install + scan | `has_delta == false` |
| Scanner waiver check + CSV report | `has_delta == false` |
| `sca-sast-stage` job (npm audit) | `has_delta == false` |
| `automated-governance` job | `has_delta == false` |
| CheckMarx / Fortify jobs | Skipped when `CX_CLIENT_SECRET` / `FOD_CLIENT_SECRET` not set (they run from `setup` in parallel, independent of `has_delta`) |

The `has_delta` flag is set by the `Compute Apex delta and infer tests` step in Job 2. It is `true` when either `package/package.xml` or `destructiveChanges/destructiveChanges.xml` contains members.

---

## Related Docs

- [Pipeline Overview](./pipeline-overview.md)
- [Manual Runbook](./manual_runbook.md)
- [SCA Waivers](./sca-waivers.md)
- [Troubleshooting](./troubleshooting.md)
