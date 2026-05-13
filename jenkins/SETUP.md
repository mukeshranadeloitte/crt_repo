# Jenkins — Salesforce UAT End-to-End Pipeline

> **Purpose:** Guide to set up the Salesforce CI/CD pipeline in any Jenkins project.
> Run the interactive setup script to generate a customised `Jenkinsfile` for your project,
> then follow the checklist to configure credentials, environment variables, and branch policies.

---

## How to Use This Guide

### Option A — Interactive Setup Script _(Recommended)_

The `setup.py` script asks you a series of questions (branches, org alias, reviewers, architects, CRT IDs, etc.) and **generates a ready-to-use `Jenkinsfile`** tailored to your project, plus a filled-in credential checklist.

**Requirements:** Python 3.8 or later (standard library only — no pip install needed)

```bash
# 1. Clone this repo (or copy the jenkins/ folder into your project)
git clone https://github.com/mukeshranadeloitte/crt_repo.git
cd crt_repo

# 2. Run the setup script
python3 jenkins/setup.py

# 3. The script will ask questions like:
#    - Project name?
#    - Jenkins URL?
#    - Which branches should the pipeline run on?  e.g. uat, main
#    - Deployment branch?                          e.g. uat
#    - Salesforce org alias?                       e.g. uat
#    - Who are the PR reviewers?                   e.g. user1, user2
#    - Who are the Architects?                     e.g. architect1, architect2
#    - CRT job/project/org IDs?
#    - Are you using CheckMarx or Fortify?
#    - SCA enforcement mode?
#
# 4. Generated files are written to:
#    jenkins/generated/Jenkinsfile              ← copy to your repo root
#    jenkins/generated/credential-checklist.md  ← your personalised setup guide
```

After running, open `jenkins/generated/credential-checklist.md` — it contains your project-specific credential IDs and a go-live checklist.

### Option B — Manual Setup

Use the manual steps in this document if you prefer not to run the script. The script automates the find-and-replace of branch names, reviewer lists, org aliases, and CRT IDs in the template Jenkinsfile.

---

## Table of Contents

1. [Pipeline Overview](#1-pipeline-overview)
2. [Prerequisites — What You Need Before Starting](#2-prerequisites--what-you-need-before-starting)
3. [Step 1 — Install Required Jenkins Plugins](#3-step-1--install-required-jenkins-plugins)
4. [Step 2 — Configure Jenkins Credentials](#4-step-2--configure-jenkins-credentials)
5. [Step 3 — Configure Environment Variables](#5-step-3--configure-environment-variables)
6. [Step 4 — Create the Multibranch Pipeline Job](#6-step-4--create-the-multibranch-pipeline-job)
7. [Step 5 — Configure GitHub Webhook](#7-step-5--configure-github-webhook)
8. [Step 6 — Set the Delta Baseline (First-Time Only)](#8-step-6--set-the-delta-baseline-first-time-only)
9. [Pipeline Stage Reference](#9-pipeline-stage-reference)
10. [How the Pipeline Works — End to End](#10-how-the-pipeline-works--end-to-end)
11. [SCA Waivers](#11-sca-waivers)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Pipeline Overview

One `Jenkinsfile` in your repository root powers this workflow.

| File | Purpose | Trigger |
|------|---------|---------|
| `Jenkinsfile` | Main CI/CD pipeline — PR validation, security scans, deployment, CRT tests | PR to `uat`/`main`; push to `uat`; manual |

**Pipeline stages:**

```
┌─────────────────────────────────────────────────────────────────┐
│  PR VALIDATION  (triggers on every PR to uat / main)            │
│                                                                 │
│  ┌─────────────┐   ┌──────────────────────┐   ┌─────────────┐  │
│  │  Evaluate   │──▶│  Salesforce PR       │   │  CheckMarx  │  │
│  │  Scanners   │   │  Validation          │   │  SAST       │  │
│  │             │   │ • Delta build         │   │ (if cred)   │  │
│  └─────────────┘   │ • Check-only deploy  │   └─────────────┘  │
│                    │ • Coverage check     │   ┌─────────────┐  │
│                    │ • SCA + waivers      │   │  Fortify    │  │
│                    │ • PR comment         │   │  SAST/DAST  │  │
│                    │ • Notify reviewers   │   │ (if cred)   │  │
│                    └──────────────────────┘   └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  DEPLOYMENT  (triggers on push / merge to uat branch)           │
│                                                                 │
│  ┌──────────────────┐   ┌──────────────────┐   ┌───────────┐   │
│  │  Architect       │──▶│  Deploy to org   │──▶│  CRT      │   │
│  │  Approval Gate   │   │  (NoTestRun)     │   │  Tests    │   │
│  │  (input step)    │   │  • Update delta  │   │           │   │
│  └──────────────────┘   └──────────────────┘   └───────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Prerequisites — What You Need Before Starting

### Tools on Jenkins Agent

| Tool | Required | Notes |
|------|----------|-------|
| **Node.js 20+** | Yes | Install via Jenkins NodeJS plugin |
| **Salesforce CLI** | Yes | Pipeline installs via `npm install -g @salesforce/cli` |
| **sfdx-git-delta** | Yes | Pipeline installs via `sf plugins install sfdx-git-delta` |
| **Salesforce Code Analyzer** | Yes | Pipeline installs via `sf plugins install @salesforce/sfdx-scanner` |
| **jq** | Yes | `apt-get install jq` on the agent |
| **curl** | Yes | Usually pre-installed on Linux agents |
| **Python 3.8+** | For running `setup.py` locally | `python3 --version` to check |
| **Git** | Yes | Agents need full clone: `git fetch --unshallow` if shallow |

### Credentials / Tokens to Obtain First

#### 1. SFDX Auth URL (Salesforce org authentication)

```bash
# Authenticate the target org locally
sf org login web --alias uat

# Retrieve the auth URL
sf org display --target-org uat --verbose
# Copy the value on the line:  Sfdx Auth Url   force://...
```

Store as `CRT_UAT_AUTHURL` → **Secret text** in Jenkins credentials.

#### 2. GitHub Personal Access Token (`GITHUB_PAT`)

Used by the pipeline to post PR comments, request reviewers, merge PRs, and update `DELTA_FROM_COMMIT`.

**Required permissions (fine-grained token):**

| Permission | Level |
|-----------|-------|
| Pull requests | Read and write |
| Contents | Read and write |
| Actions variables | Read and write |

> **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**

#### 3. CRT API Token _(if using Copado Robotic Testing)_

**Copado → Settings → External Personal Access Tokens → New Token**

Copy immediately — shown only once. Store as `CRT_API_TOKEN` in Jenkins.

#### 4. CheckMarx / Fortify credentials _(optional)_

Obtain from your security team. Store as separate secret text credentials in Jenkins.

---

## 3. Step 1 — Install Required Jenkins Plugins

**Jenkins → Manage Jenkins → Plugins → Available plugins**

### Required

| Plugin | Purpose |
|--------|---------|
| **Pipeline** | Core Jenkinsfile execution |
| **GitHub Branch Source** | Multibranch pipeline, PR detection |
| **NodeJS** | Node.js toolchain on agents |
| **Credentials Binding** | Bind credentials to env vars in pipeline |
| **GitHub** | GitHub webhook integration |
| **AnsiColor** | Coloured console output |
| **Timestamper** | Timestamp log lines |
| **Workspace Cleanup** | Clean workspace between builds |

### Optional

| Plugin | Purpose |
|--------|---------|
| **CheckMarx** | Native CheckMarx AST integration |
| **Fortify** | Fortify on Demand integration |
| **Blue Ocean** | Improved pipeline visualisation |
| **Slack Notification** | Post results to Slack channel |

---

## 4. Step 2 — Configure Jenkins Credentials

**Jenkins → Manage Jenkins → Credentials → System → Global credentials → Add Credential**

> All credentials must be of Kind: **Secret text** unless noted otherwise.

### Required Credentials

| Credential ID | Kind | How to Get |
|--------------|------|-----------|
| `CRT_UAT_AUTHURL` | Secret text | `sf org display --target-org <alias> --verbose` |
| `GITHUB_PAT` | Secret text | GitHub fine-grained PAT — see [Prerequisites](#2-prerequisites--what-you-need-before-starting) |
| `CRT_API_TOKEN` | Secret text | Copado → Settings → External Personal Access Tokens |

### Optional Credentials (Security Scanners)

| Credential ID | Kind | Scanner |
|--------------|------|---------|
| `CX_CLIENT_SECRET` | Secret text | CheckMarx |
| `CX_BASE_URI` | Secret text | CheckMarx |
| `CX_TENANT` | Secret text | CheckMarx |
| `CX_CLIENT_ID` | Secret text | CheckMarx |
| `FOD_CLIENT_SECRET` | Secret text | Fortify |
| `FOD_CLIENT_ID` | Secret text | Fortify |
| `FOD_APP_NAME` | Secret text | Fortify |
| `FOD_RELEASE_NAME` | Secret text | Fortify |
| `FOD_DAST_SCAN_URL` | Secret text | Fortify DAST (optional) |

> ⚠️ **Credential IDs must match exactly** — the Jenkinsfile references them by these exact string IDs.

---

## 5. Step 3 — Configure Environment Variables

**Jenkins → Manage Jenkins → Configure System → Global properties → ✅ Environment variables**

### Must Set Before First Run

| Variable | Notes |
|----------|-------|
| `DELTA_FROM_COMMIT` | SHA of last deployed commit — **set this before the first pipeline run** (see [Step 6](#8-step-6--set-the-delta-baseline-first-time-only)) |

### Configurable (have sensible defaults in Jenkinsfile)

| Variable | Default | Description |
|----------|---------|-------------|
| `ORG_ALIAS` | `uat` | Salesforce org alias |
| `COVERAGE_THRESHOLD` | `85` | Minimum Apex coverage % (1–100) |
| `SOURCE_DIR` | `force-app/main/default` | Salesforce source directory |
| `SCA_ENFORCEMENT_MODE` | `enforce` | `enforce` / `warn` / `off` — see [SCA Waivers](#11-sca-waivers) |
| `CRT_JOB_ID` | *(yours)* | From Copado CRT → your test job |
| `CRT_PROJECT_ID` | *(yours)* | From Copado CRT → project |
| `CRT_ORG_ID` | *(yours)* | From Copado CRT → org |
| `GITHUB_REPO` | *(yours)* | `owner/repo` e.g. `mukeshranadeloitte/crt_repo` |
| `GITHUB_API_URL` | `https://api.github.com` | Override for GitHub Enterprise |

---

## 6. Step 4 — Create the Multibranch Pipeline Job

1. **Jenkins → New Item**
2. Enter name: `Salesforce UAT E2E Pipeline`
3. Select: **Multibranch Pipeline** → OK
4. **Branch Sources → Add source → GitHub**
   - Credentials: select `GITHUB_PAT`
   - Repository HTTPS URL: `https://github.com/<org>/<repo>.git`
5. **Build Configuration**
   - Mode: `by Jenkinsfile`
   - Script Path: `Jenkinsfile`
6. **Scan Multibranch Pipeline Triggers**
   - ✅ Periodically if not otherwise run: `1 minute`
   - *(Webhook preferred — see Step 5)*
7. **Orphaned Item Strategy** → Discard old items: Days to keep: `7`
8. Click **Save**

Jenkins will immediately scan and discover all branches and open PRs.

> **Note:** Pull request branches appear as `PR-<number>` in Blue Ocean. The environment variable `CHANGE_ID` contains the PR number when running on a PR branch.

---

## 7. Step 5 — Configure GitHub Webhook

Webhooks trigger Jenkins immediately on PR events, instead of waiting for polling.

1. **GitHub repo → Settings → Webhooks → Add webhook**
2. **Payload URL:** `https://<your-jenkins-url>/github-webhook/`
3. **Content type:** `application/json`
4. **Which events** → Select individual events:
   - ✅ Pull requests
   - ✅ Pull request reviews
   - ✅ Pushes
5. ✅ Active
6. Click **Add webhook**

Verify delivery in **GitHub → Settings → Webhooks → Recent Deliveries** — should show HTTP 200.

> For Jenkins behind a firewall: use **GitHub Enterprise Server**, a **reverse proxy**, or **ngrok** for testing.

---

## 8. Step 6 — Set the Delta Baseline (First-Time Only)

`DELTA_FROM_COMMIT` is the SHA of the last commit that was deployed to the Salesforce org. The pipeline builds a delta of only changed components since this SHA.

```bash
# Get the current tip of your deployment branch
git checkout uat
git rev-parse HEAD
# Example:  a1b2c3d4e5f6789012345678901234567890abcd
```

Set this in Jenkins:
1. **Jenkins → Manage Jenkins → Configure System → Environment variables**
2. Set `DELTA_FROM_COMMIT` = the SHA above
3. Save

> After first setup, every successful deployment **automatically updates** `DELTA_FROM_COMMIT` via the GitHub Variables API (`GITHUB_PAT` required). If `GITHUB_PAT` is not set, the pipeline warns and you must update manually.

---

## 9. Pipeline Stage Reference

### PR Validation Stages _(triggered by PR open/update)_

| Stage | What It Does | Condition |
|-------|-------------|-----------|
| **Evaluate Scanner Availability** | Checks which scanner credentials are configured; sets `runCheckmarx` / `runFortify` flags | Every PR |
| **Request PR Reviewers** | Auto-requests configured reviewers via GitHub API (excludes PR author) | Every PR |
| **Salesforce PR Validation** | Delta build → check-only deploy → coverage check → SCA scan → waiver check → PR comment → notify reviewers | PR to target branches |
| **CheckMarx SAST** | Full SAST scan; uploads SARIF to GitHub Code Scanning | PR; only if `CX_CLIENT_SECRET` credential set |
| **Fortify SAST/DAST** | SAST + optional DAST scan; uploads SARIF | PR; only if `FOD_CLIENT_SECRET` credential set |

### Deployment Stages _(triggered by push/merge to deployment branch)_

| Stage | What It Does | Condition |
|-------|-------------|-----------|
| **Architect Approval Gate** | Jenkins `input` step — only architects can click Proceed; main-branch only | Push to deployment branch |
| **Deploy to UAT org** | Delta deploy (`NoTestRun` — tests ran in PR validation); polls for completion | After gate approval |
| **Update Delta Baseline** | Updates `DELTA_FROM_COMMIT` via GitHub Variables API | After successful deploy |
| **Trigger CRT Tests** | Fires Copado Robotic Testing job; polls status every 30s; posts summary PR comment | After successful deploy |

---

## 10. How the Pipeline Works — End to End

### PR Validation Flow

```
Developer opens PR (feature → uat  OR  uat → main)
        │
        ▼
[GitHub webhook triggers Jenkins on PR branch]
        │
        ├─ Checkout full git history (--unshallow)
        ├─ Install Salesforce CLI + sfdx-git-delta
        ├─ Authenticate Salesforce org (CRT_UAT_AUTHURL)
        ├─ Extract test classes from PR description (Tests: Class1, Class2)
        ├─ Build delta: changed components since DELTA_FROM_COMMIT
        ├─ Check-only deploy (--dry-run) → poll every 15s → live progress
        ├─ Check Apex test coverage (>= COVERAGE_THRESHOLD %)
        ├─ Install Salesforce Code Analyzer
        ├─ Fetch SCA waivers from main branch (tamper-proof)
        ├─ Run sf scanner run on changed .cls/.trigger/.js/.html files
        ├─ Evaluate violations against waivers (expired = FAIL in enforce mode)
        ├─ Post SCA governance report as PR comment
        └─ Post "✅ All checks passed — ready for review" comment to PR
```

### Test Class Resolution Priority

1. **PR description** — add `Tests: ClassName1, ClassName2` anywhere in the PR body
2. **Naming convention** — classes matching `*Test`, `*Tests`, `*TestClass` for each changed class
3. **`@isTest` annotation** — scans changed `.cls` files for the annotation
4. **No Apex changed** — skips test execution (`NoTestRun`)

### Deployment Flow

```
PR approved and merged (or direct push to uat branch)
        │
        ▼
[Push event triggers Jenkins on uat branch]
        │
        ├─ Architect Gate: Jenkins input() step
        │     Architects: chorevathi-deloitte, mukeshranadeloitte
        │     Timeout: 7 days
        │     (main-branch only; uat skips architect gate)
        │
        ├─ Checkout full history
        ├─ Install SF CLI + sfdx-git-delta
        ├─ Authenticate org
        ├─ Build delta: DELTA_FROM_COMMIT → HEAD
        ├─ Deploy with --test-level NoTestRun (tests already validated)
        │     └─ Poll every 15s → live progress table
        ├─ Update DELTA_FROM_COMMIT → deployed commit SHA (via GitHub API)
        └─ Trigger CRT Tests → poll every 30s → post summary
```

### Delta Calculation

```
PR Validation:
  FROM: git merge-base HEAD origin/<target-branch>   ← PR base commit
  TO:   HEAD                                          ← latest PR commit

Deployment:
  FROM: DELTA_FROM_COMMIT                             ← last deployed SHA
  TO:   HEAD                                          ← current branch tip
```

---

## 11. SCA Waivers

Violations can be waived by editing `.github/sf-scanner-waivers.csv` **on the main branch only**.

> **Important:** The pipeline always reads waivers from the `main` branch via GitHub API — changes in feature branches are ignored. Only commits merged to `main` take effect.

### Waiver File Format

File path: `.github/sf-scanner-waivers.csv`

```csv
rule,file_pattern,message_contains,severity_threshold,expiry,reason,approved_by,approved_date,ticket,status
ApexDoc,CoverageDemoService.cls,,3,09-04-2025,Missing ApexDoc — refactoring in progress.,jane-techlead,01-04-2025,PROJ-123,ACTIVE
```

| Column | Required | Description |
|--------|----------|-------------|
| `rule` | ✅ | Rule name substring (e.g. `ApexDoc`). Blank/`*` = all rules for this file |
| `file_pattern` | ✅ | Filename substring (e.g. `MyClass.cls`). Blank/`*` = all files for this rule |
| `message_contains` | ⬜ | Optional violation message substring |
| `severity_threshold` | ⬜ | Only waive at this severity or above (blank = any) |
| `expiry` | ✅ | `DD-MM-YYYY` preferred; also `DD/MM/YYYY`, `YYYY-MM-DD` |
| `reason` | ✅ | Business justification with Jira/ticket reference |
| `approved_by` | ✅ | GitHub username of approver |
| `approved_date` | ✅ | Approval date |
| `ticket` | ✅ | Jira/GitHub issue ID |
| `status` | ✅ | `ACTIVE` = active; `REVOKED` = retired (keep row — never delete) |

### SCA Enforcement Modes (`SCA_ENFORCEMENT_MODE`)

| Mode | Behaviour |
|------|----------|
| `enforce` | ❌ Fails if expired waivers found |
| `warn` | ⚠️ All violations logged as warnings; pipeline continues |
| `off` | ⏭️ All SCA steps skipped entirely |

> **Tip:** Use `off` during initial project setup; switch to `enforce` once the codebase is clean.

### Waiver Status Values

| Status | Meaning |
|--------|---------|
| ✅ `WAIVED` | Active waiver, >30 days remaining — violation suppressed |
| ⏰ `WAIVED_EXPIRING_SOON` | Active but ≤30 days left — fix or renew |
| ❌ `EXPIRED_WAIVER` | Past expiry date — **fails in enforce mode** |
| ⚠️ `VIOLATION` | No matching waiver — warning only in enforce mode |

---

## 12. Troubleshooting

### Pipeline doesn't trigger on PR

- Check webhook in **GitHub → repo → Settings → Webhooks → Recent Deliveries** shows HTTP 200
- Check Jenkins is reachable from GitHub (network/firewall/proxy)
- Force a scan: **Jenkins → pipeline job → Scan Multibranch Pipeline Now**
- Confirm the Jenkinsfile path in the job config matches the file location in repo

---

### `DELTA_FROM_COMMIT` not set or empty

Follow [Step 6](#8-step-6--set-the-delta-baseline-first-time-only). Must be set before the first deployment run.

---

### Salesforce authentication fails

- Check `CRT_UAT_AUTHURL` credential in Jenkins — must be complete `force://` URL
- SFDX auth URL may have expired. Re-generate:
  ```bash
  sf org display --target-org <alias> --verbose
  ```
- Update the Jenkins credential and re-run

---

### Check-only deploy fails with component errors

- Run locally to diagnose:
  ```bash
  sf project deploy start --dry-run --manifest package/package.xml --target-org <alias>
  ```
- Check component API versions match the target org

---

### Coverage check fails

- Add `Tests: ClassName` to your PR description
- Verify the test class exercises the changed production class
- Adjust `COVERAGE_THRESHOLD` in Jenkins environment variables

---

### Architect `input` step times out

Default timeout is 7 days. If it times out, the deployment stage is aborted without affecting the org. Re-trigger by re-running the deployment stage in Jenkins or pushing a new commit.

To change the timeout: edit `timeout(time: 7, unit: 'DAYS')` in the `Architect Approval Gate` stage in the Jenkinsfile.

---

### `GITHUB_PAT` permissions error on PR comment / variable update

Ensure the PAT has:
- Pull requests: **Read and write**
- Contents: **Read and write**
- Actions variables: **Read and write** (for `DELTA_FROM_COMMIT` auto-update)

---

### CheckMarx or Fortify stage always skipped

- Confirm the credential **ID** in Jenkins exactly matches: `CX_CLIENT_SECRET` / `FOD_CLIENT_SECRET`
- Confirm credential **Kind** is `Secret text` (not `Username with password`)
- In the Jenkinsfile `Evaluate Scanner Availability` stage, check that credential binding returns a non-empty value

---

## Quick Start Checklist

```
□ Ran jenkins/setup.py and reviewed generated Jenkinsfile
□ Required Jenkins plugins installed (Pipeline, GitHub Branch Source, NodeJS, Credentials Binding)
□ CRT_UAT_AUTHURL secret text credential created
□ GITHUB_PAT secret text credential created with correct permissions
□ CRT_API_TOKEN secret text credential created
□ DELTA_FROM_COMMIT global environment variable set to current branch tip SHA
□ Multibranch Pipeline job created, pointed to Jenkinsfile in repo root
□ GitHub webhook configured → verified HTTP 200 in GitHub webhook deliveries
□ Salesforce CLI + jq available on Jenkins agent
□ Test PR opened and PR validation pipeline triggered successfully
□ Deployment stage tested: architect input() step appears for main branch
□ SCA waiver file exists at .github/sf-scanner-waivers.csv on main branch
□ DELTA_FROM_COMMIT auto-updates after first successful deployment
```
