# Azure DevOps — Salesforce UAT End-to-End Pipeline

> **Purpose:** Guide to set up the Salesforce CI/CD pipeline in any Azure DevOps project.
> Run the interactive setup script to generate a customised pipeline YAML for your project,
> then follow the checklist to configure variables, secrets, and branch policies.

---

## How to Use This Guide

### Option A — Interactive Setup Script _(Recommended)_

The `setup.py` script asks you a series of questions (branches, org alias, reviewers, architects, etc.) and **generates a ready-to-use pipeline YAML** tailored to your project, plus a filled-in variable checklist.

**Requirements:** Python 3.8 or later (standard library only — no pip install needed)

```bash
# 1. Clone this repo (or copy the ado-pipelines/ folder into your project)
git clone https://github.com/mukeshranadeloitte/crt_repo.git
cd crt_repo

# 2. Run the setup script
python3 ado-pipelines/setup.py

# 3. The script will ask questions like:
#    - Project name?
#    - ADO organisation and project?
#    - Which branches should the pipeline run on?  e.g. uat, main
#    - Deployment branch?                          e.g. uat
#    - Salesforce org alias?                       e.g. uat
#    - Who are the PR reviewers?                   e.g. user1, user2
#    - Who are the Architects?                     e.g. user1, user2
#    - CRT job/project/org IDs?
#    - Are you using CheckMarx or Fortify?
#
# 4. Generated files are written to:
#    ado-pipelines/generated/e2e-pipeline.yml          ← copy to your repo
#    ado-pipelines/generated/update-delta-on-push.yml  ← copy to your repo
#    ado-pipelines/generated/variable-checklist.md     ← your personalised setup guide
```

After running, open `ado-pipelines/generated/variable-checklist.md` — it contains your project-specific variable values and a go-live checklist.

### Option B — Manual Setup

Use the manual steps in this document if you prefer not to run the script. The script just automates the find-and-replace of branch names, reviewer lists, and org aliases in the template YAML files.

---

## Table of Contents

1. [Pipeline Overview](#1-pipeline-overview)
2. [Prerequisites — What You Need Before Starting](#2-prerequisites--what-you-need-before-starting)
3. [Step 1 — Create the Variable Group](#3-step-1--create-the-variable-group)
4. [Step 2 — Create the ADO Environment (Architect Approval Gate)](#4-step-2--create-the-ado-environment-architect-approval-gate)
5. [Step 3 — Register the Pipelines in ADO](#5-step-3--register-the-pipelines-in-ado)
6. [Step 4 — Configure Branch Policies](#6-step-4--configure-branch-policies)
7. [Step 5 — Set the Delta Baseline (First-Time Only)](#7-step-5--set-the-delta-baseline-first-time-only)
8. [Pipeline Job Reference](#8-pipeline-job-reference)
9. [How the Pipeline Works — End to End](#9-how-the-pipeline-works--end-to-end)
10. [SCA Waivers](#10-sca-waivers)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Pipeline Overview

Two YAML pipeline files power this workflow:

| File | Purpose | Trigger |
|------|---------|---------|
| `ado-pipelines/e2e-pipeline.yml` | Main CI/CD pipeline — PR validation, security scans, deployment, CRT tests | PR to `uat`/`main`; manual |
| `ado-pipelines/update-delta-on-push.yml` | Keeps delta baseline current on every UAT push | Every push to `uat` |

**Pipeline stages:**

```
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 1: PR VALIDATION  (triggers on every PR to uat / main)   │
│                                                                 │
│  ┌─────────────┐   ┌──────────────────────┐   ┌─────────────┐ │
│  │   setup     │──▶│ salesforce_validation │   │  checkmarx  │ │
│  │ (scanner    │   │ • Delta build         │   │  _sast      │ │
│  │  eval)      │   │ • Check-only deploy   │   │ (if secret) │ │
│  └─────────────┘   │ • Coverage check      │   └─────────────┘ │
│         │          │ • SCA + waivers       │   ┌─────────────┐ │
│         └──────────│ • PR comment          │   │  fortify    │ │
│                    │ • Notify reviewers    │   │  _sast_dast │ │
│                    └──────────────────────┘   │ (if secret) │ │
│                                               └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  STAGE 2: DEPLOYMENT  (manual trigger after PR approved)         │
│                                                                 │
│  ┌──────────────────┐   ┌──────────────────┐   ┌───────────┐  │
│  │ approval_merge   │──▶│ deploy_after_    │──▶│ trigger_  │  │
│  │ _gate            │   │ merge            │   │ crt_tests │  │
│  │ (ADO Environment │   │ • Delta deploy   │   │           │  │
│  │  approval gate)  │   │ • NoTestRun      │   └───────────┘  │
│  └──────────────────┘   │ • Update delta   │                   │
│                         │   baseline       │                   │
│                         └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Prerequisites — What You Need Before Starting

Gather the following before running the setup script or starting manual setup.

### Tools

| Tool | Required | Notes |
|------|----------|-------|
| **Python 3.8+** | For running `setup.py` | `python3 --version` to check |
| **Git** | Yes | To checkout full history (`fetch-depth: 0`) |
| **Salesforce CLI** | Installed by pipeline | `npm install --global @salesforce/cli` runs in the pipeline agent |
| **sfdx-git-delta** | Installed by pipeline | Pipeline installs via `sf plugins install sfdx-git-delta` |
| **Salesforce Code Analyzer** | Installed by pipeline | Pipeline installs via `sf plugins install @salesforce/sfdx-scanner` |

### Credentials / Tokens You Must Obtain

#### 1. SFDX Auth URL (for Salesforce org authentication)

```bash
# Authenticate the target org locally first
sf org login web --alias uat

# Then retrieve the auth URL
sf org display --target-org uat --verbose
# Look for the line:  Sfdx Auth Url   force://...
# Copy the full value starting with "force://"
```

Store this as the `CRT_UAT_AUTHURL` secret in the variable group.

#### 2. Azure DevOps Personal Access Token (ADO_PAT)

The pipeline uses this token to:
- Add PR reviewers
- Post PR comments
- Update the `DELTA_FROM_COMMIT` variable after deployment

**Required scopes when creating the PAT:**

| Scope | Permission |
|-------|-----------|
| Code | Read |
| Build | Read & Execute |
| Variable Groups | Read & Manage |
| Pull Request Threads | Read & Write |
| Identity | Read |

> Go to **ADO → User Settings (top right) → Personal access tokens → New Token**

#### 3. CRT API Token _(if using Copado Robotic Testing)_

Go to **Copado → Settings → External Personal Access Tokens → New Token**

Copy the token value — it can only be seen once.

#### 4. CheckMarx / Fortify credentials _(optional)_

Only needed if your project uses these scanners. Obtain from your security team.

---

## 3. Step 1 — Create the Variable Group

All pipeline configuration lives in an ADO **Library Variable Group**.

1. Go to **Pipelines → Library → + Variable group**
2. Name it exactly: `salesforce-uat`
3. Add the variables below (mark secrets as secret by clicking the lock icon)

### Salesforce Variables

| Variable | Example Value | Secret? | How to get it |
|----------|--------------|---------|--------------|
| `ORG_ALIAS` | `uat` | No | Your Salesforce org alias |
| `DELTA_FROM_COMMIT` | _(set in Step 5)_ | No | SHA of last deployed commit to target branch |
| `COVERAGE_THRESHOLD` | `85` | No | Minimum Apex code coverage % (1–100) |
| `SOURCE_DIR` | `force-app/main/default` | No | Relative path to Salesforce source |
| `SCA_ENFORCEMENT_MODE` | `enforce` | No | `enforce` / `warn` / `off` — see [SCA section](#10-sca-waivers) |
| `CRT_UAT_AUTHURL` | `force://...` | **✅ Yes** | `sf org display --target-org <alias> --verbose` |

### ADO Variables

| Variable | Example Value | Secret? | Notes |
|----------|--------------|---------|-------|
| `ADO_PAT` | _(token)_ | **✅ Yes** | Personal Access Token — see [Prerequisites](#2-prerequisites--what-you-need-before-starting) |
| `DEPLOY_PIPELINE_ID` | `42` | No | Fill after Step 3 — pipeline definition ID from ADO URL |
| `VARIABLE_GROUP_ID` | `7` | No | Visible in URL after saving: `...variableGroups?groupId=7` |

### CRT Variables _(skip if not using CRT)_

| Variable | Example Value | Secret? | How to get it |
|----------|--------------|---------|--------------|
| `CRT_API_TOKEN` | _(token)_ | **✅ Yes** | Copado → Settings → External Personal Access Tokens |
| `CRT_JOB_ID` | `115686` | No | Copado CRT → your test job ID |
| `CRT_PROJECT_ID` | `73283` | No | Copado CRT → project ID |
| `CRT_ORG_ID` | `43532` | No | Copado CRT → org ID |

### CheckMarx Variables _(skip if not using CheckMarx)_

| Variable | Secret? |
|----------|---------|
| `CX_BASE_URI` | **✅ Yes** |
| `CX_TENANT` | **✅ Yes** |
| `CX_CLIENT_ID` | **✅ Yes** |
| `CX_CLIENT_SECRET` | **✅ Yes** |
| `CX_PROJECT_NAME` | No |

### Fortify Variables _(skip if not using Fortify)_

| Variable | Secret? |
|----------|---------|
| `FOD_URL` | No |
| `FOD_CLIENT_ID` | **✅ Yes** |
| `FOD_CLIENT_SECRET` | **✅ Yes** |
| `FOD_APP_NAME` | **✅ Yes** |
| `FOD_RELEASE_NAME` | **✅ Yes** |

4. After saving, note the **Variable Group ID** from the URL: `...variableGroups?groupId=XX`
   → Update `VARIABLE_GROUP_ID` in the group to this number.

---

## 4. Step 2 — Create the ADO Environment (Architect Approval Gate)

The deployment stage requires an ADO **Environment** with approval gates so only architects can approve a deployment.

1. **Pipelines → Environments → New environment**
2. **Name:** `uat-deployment` _(or the name you chose in setup.py)_
3. **Resource:** None
4. Click **Create**
5. Open the environment → **⋮ → Approvals and checks → + → Approvals**
6. **Add approvers** — add each architect's ADO username:
   - `chorevathi-deloitte`
   - `mukeshranadeloitte`
7. **Instructions to approvers:** `Architect approval required. Verify all PR checks passed before approving.`
8. **Timeout:** 7 days
9. Click **Create**

> **Note:** The pipeline YAML also enforces the architect list in code for `main`-branch deployments. Both layers of protection are active.

---

## 5. Step 3 — Register the Pipelines in ADO

### 5.1 Register the Main E2E Pipeline

1. **Pipelines → New pipeline**
2. Select **Azure Repos Git** → select your repository
3. Select **Existing Azure Pipelines YAML file**
4. Branch: `main` | Path: `/ado-pipelines/e2e-pipeline.yml`
   _(if you used setup.py, copy generated files to your repo first)_
5. Click **Continue → Save** (do not Run yet)
6. Rename the pipeline to: `Salesforce UAT E2E Pipeline`
7. Note the **Pipeline Definition ID** from the URL: `.../_build?definitionId=42`
   → Set `DEPLOY_PIPELINE_ID` to this number in the variable group

### 5.2 Register the Delta Baseline Updater

1. **Pipelines → New pipeline → Azure Repos Git → your repo**
2. Path: `/ado-pipelines/update-delta-on-push.yml`
3. Click **Continue → Save**
4. Rename to: `Update Delta Baseline on UAT Push`

### 5.3 Link the Variable Group to Both Pipelines

For **each** pipeline:
1. Open the pipeline → **Edit → Variables → Variable groups**
2. Click **Link variable group** → select `salesforce-uat`
3. Save

---

## 6. Step 4 — Configure Branch Policies

Set branch policies on your target branches (`uat`, `main`) to require the pipeline to pass before merging.

1. **Project Settings → Repos → Branches**
2. Click `...` next to `uat` → **Branch policies**
3. **Build validation → + Add build policy**:
   - **Build pipeline:** `Salesforce UAT E2E Pipeline`
   - **Trigger:** Automatic
   - **Policy requirement:** Required
   - **Display name:** `Salesforce PR Validation`
4. Click **Save**
5. Repeat for `main` branch

**Recommended additional policies (both branches):**
- ✅ Require a minimum number of reviewers: 1
- ✅ Block direct pushes to main
- ✅ Check for linked work items (optional)

---

## 7. Step 5 — Set the Delta Baseline (First-Time Only)

`DELTA_FROM_COMMIT` tells the pipeline where to start the delta calculation — it should be the SHA of the last commit that was deployed to the target org.

```bash
# Get the current tip of your deployment branch
git checkout uat
git rev-parse HEAD
# Example:  a1b2c3d4e5f6789012345678901234567890abcd
```

1. **Pipelines → Library → salesforce-uat**
2. Find `DELTA_FROM_COMMIT` → set the value to the SHA above
3. Save

> After first setup, every deployment automatically updates `DELTA_FROM_COMMIT` to the deployed SHA. The `update-delta-on-push.yml` pipeline also updates it on any direct push to the UAT branch.

---

## 8. Pipeline Job Reference

### Stage 1: PR Validation

| Job | What it does | Runs when |
|-----|-------------|-----------|
| **Evaluate Scanner Availability** | Checks which security scanners are configured | Every PR |
| **Salesforce PR validation** | Delta build → check-only deploy → coverage check → SCA → reviewer notify | PR to target branches |
| **CheckMarx AST Scan** | SAST scan | PR; only if `CX_CLIENT_SECRET` is set |
| **Fortify on Demand Scan** | SAST/DAST scan | PR; only if `FOD_CLIENT_SECRET` is set |

### Stage 2: Deployment

| Job | What it does | Runs when |
|-----|-------------|-----------|
| **Approval + Merge Gate** | Waits for architect approval via ADO Environment | Manual trigger |
| **Deploy merged commit** | Delta deploy (`NoTestRun` — tests ran in validation) | After gate approved |
| **Trigger CRT Tests** | Runs CRT test job, polls for result, posts summary | After deployment succeeds |

---

## 9. How the Pipeline Works — End to End

### PR Validation Flow

```
Developer opens PR (feature → uat  OR  uat → main)
        │
        ▼
[Pipeline auto-triggers via branch policy]
        │
        ├─ Request reviewers via ADO API (excluding PR author)
        ├─ Checkout full git history
        ├─ Authenticate Salesforce org (SFDX auth URL)
        ├─ Build delta: changed components since DELTA_FROM_COMMIT
        ├─ Check-only deploy to org (--dry-run)
        │     └─ Poll for completion; show component/test progress table
        ├─ Check Apex test coverage (threshold: COVERAGE_THRESHOLD %)
        ├─ Run Salesforce Code Analyzer (sf scanner run)
        ├─ Evaluate violations against sf-scanner-waivers.csv (from main)
        ├─ Post SCA governance report as PR comment
        └─ Notify reviewers: "✅ All checks passed — ready for review"
```

### Test Class Resolution Priority

The pipeline resolves test classes in this order:

1. **PR description** — add `Tests: ClassName1, ClassName2` anywhere in the PR body
2. **Inferred by naming convention** — classes matching `*Test`, `*Tests`, `*TestClass` for each changed class
3. **`@isTest` annotation** — scans changed `.cls` files for the annotation
4. **No Apex changed** — skips test execution (`NoTestRun`)

### Deployment Flow

```
Architect approves the deployment request in ADO
        │
        ▼
[Deployment stage triggers]
        │
        ├─ Architect gate: validate approver is in ARCHITECTS list (main branch only)
        ├─ Rebuild delta: DELTA_FROM_COMMIT → HEAD
        ├─ Deploy to org (--test-level NoTestRun — tests already validated)
        │     └─ Poll for completion
        ├─ Update DELTA_FROM_COMMIT → deployed commit SHA
        └─ Trigger CRT automated tests → poll → post summary
```

---

## 10. SCA Waivers

Violations can be waived by editing `.github/sf-scanner-waivers.csv`.

> **Important:** The pipeline always reads waivers from the `main` branch — changes in feature branches are ignored. Only commits merged to `main` take effect.

### Waiver File Format

File path: `.github/sf-scanner-waivers.csv`

```csv
Component,Rule,Description,ExpiryDate,Status
force-app/main/default/classes/CoverageDemoService.cls,ApexDoc,Missing ApexDoc comment,2025-09-09,ACTIVE
```

| Column | Description |
|--------|-------------|
| `Component` | File path (partial match) — leave blank to match all files |
| `Rule` | Scanner rule name e.g. `ApexDoc`, `AvoidGlobalModifier` |
| `Description` | Human-readable reason for the waiver |
| `ExpiryDate` | `YYYY-MM-DD` — waiver expires on this date |
| `Status` | `ACTIVE` = active; `REVOKED` = waiver removed |

### SCA Enforcement Modes

| Mode | Behavior |
|------|---------|
| `enforce` | ❌ Fails if expired waivers or unwaived violations found |
| `warn` | ⚠️ Reports violations as warnings; pipeline continues |
| `off` | Skips all SCA steps |

### Waiver Summary Table (in PR comment)

| State | Meaning |
|-------|---------|
| ✅ Waived (active) | Valid waiver — violation suppressed |
| ⏰ Expiring ≤30 days | Active but expiring soon — fix or renew |
| ❌ Expired | Waiver date passed — **fails in enforce mode** |
| ⚠️ Unwaived | No matching waiver — **fails in enforce mode** |

---

## 11. Troubleshooting

### Pipeline doesn't trigger on PR

- Check that the branch policy is **Required** on the target branch
- Check that the PR touches `force-app/**` — PRs only changing docs won't trigger (by path filter design)

---

### `DELTA_FROM_COMMIT` not set or empty

Follow [Step 5](#7-step-5--set-the-delta-baseline-first-time-only) to set the baseline SHA. This must be done once on first setup.

---

### Salesforce authentication fails

- Check `CRT_UAT_AUTHURL` secret is not empty in the variable group
- The SFDX auth URL may have expired (connected app session). Re-generate:
  ```bash
  sf org display --target-org <alias> --verbose
  ```

---

### Check-only deploy fails with component errors

- Run locally to diagnose: `sf project deploy start --dry-run --manifest package/package.xml --target-org <alias>`
- Check that changed components exist in the target org's API version

---

### Coverage check fails

- Add `Tests: ClassName` to your PR description
- Ensure the test class exercises the changed production class
- Adjust `COVERAGE_THRESHOLD` in the variable group if needed

---

### Architect gate fails

Only architects can approve main-branch deployments. To add an architect, edit **both**:

1. `ARCHITECTS` array in `ado-pipelines/e2e-pipeline.yml`
2. Approvers list in the `uat-deployment` ADO Environment

---

### `ADO_PAT` permissions error

Ensure the PAT has:

| Scope | Permission needed |
|-------|-----------------|
| Code | Read |
| Build | Read & Execute |
| Variable Groups | Read & Manage |
| Pull Request Threads | Read & Write |
| Identity | Read |

---

### `DELTA_FROM_COMMIT` not updating after deployment

The pipeline updates this via ADO REST API. If it fails:

1. Verify `ADO_PAT` has Variable Groups: Read & Manage
2. Verify `DEPLOY_PIPELINE_ID` matches the actual pipeline definition ID
3. Manual fallback: run `git rev-parse HEAD` on the deployment branch and update the variable group manually

---

## Quick Start Checklist

```
□ Ran setup.py and reviewed generated files
□ Variable group 'salesforce-uat' created with all variables
□ CRT_UAT_AUTHURL secret set (SFDX auth URL)
□ ADO_PAT secret set with correct scopes
□ ADO Environment 'uat-deployment' created with approval gates
□ Architect approvers added to environment
□ e2e-pipeline.yml registered as pipeline in ADO
□ update-delta-on-push.yml registered as pipeline in ADO
□ Variable group linked to both pipelines
□ DEPLOY_PIPELINE_ID and VARIABLE_GROUP_ID updated in variable group
□ Branch policy added to all target branches
□ DELTA_FROM_COMMIT set to current deployment branch tip SHA
□ SCA waiver file at .github/sf-scanner-waivers.csv on main branch
□ Test PR opened and pipeline triggered successfully
```
