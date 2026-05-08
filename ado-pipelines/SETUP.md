# Azure DevOps — Salesforce UAT End-to-End Pipeline

> **Purpose:** Step-by-step guide to set up the Salesforce CI/CD pipeline in your Azure DevOps project. Covers all prerequisites, variable configuration, pipeline registration, and branch protection rules.

---

## Table of Contents

1. [Pipeline Overview](#1-pipeline-overview)
2. [Prerequisites](#2-prerequisites)
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
| `ado-pipelines/e2e-uat-pipeline.yml` | Main CI/CD pipeline — PR validation, security scans, deployment, CRT tests | PR to `uat`/`main`; manual |
| `ado-pipelines/update-delta-on-uat-push.yml` | Keeps delta baseline current on every UAT push | Every push to `uat` |

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
│  │  approval gate)  │   │ • NoTestRun      │   │           │  │
│  └──────────────────┘   │ • Update delta   │   └───────────┘  │
│                         │   baseline       │                   │
│                         └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Prerequisites

Ensure the following tools and access are in place before starting:

| Requirement | Details |
|-------------|---------|
| **Salesforce CLI** | Installed on build agents via `npm install --global @salesforce/cli` (pipeline handles this) |
| **sfdx-git-delta** | Installed by pipeline via `sf plugins install sfdx-git-delta` |
| **Salesforce Code Analyzer** | Installed by pipeline via `sf plugins install @salesforce/sfdx-scanner` |
| **ADO Personal Access Token** | Scope: `Code (Read)`, `Build (Read & Execute)`, `Variable Groups (Read & Manage)`, `Pull Request Threads (Read & Write)` |
| **SF SFDX Auth URL** | Generate via `sf org display --target-org <alias> --verbose` → copy the `Sfdx Auth Url` |
| **CRT API Token** | Copado Robotic Testing External Personal Access Token from Copado settings |

---

## 3. Step 1 — Create the Variable Group

All secrets and configuration are stored in an ADO **Library Variable Group** named `salesforce-uat`.

### 3.1 Create the Variable Group

1. Go to **Pipelines → Library → + Variable group**
2. Name it exactly: `salesforce-uat`
3. Add the following variables:

#### Salesforce Variables

| Variable Name | Value | Secret? |
|---------------|-------|---------|
| `ORG_ALIAS` | `uat` (or your org alias) | No |
| `DELTA_FROM_COMMIT` | _(set in Step 5)_ | No |
| `COVERAGE_THRESHOLD` | `85` | No |
| `SOURCE_DIR` | `force-app/main/default` | No |
| `SCA_ENFORCEMENT_MODE` | `enforce` | No |
| `CRT_UAT_AUTHURL` | _(SFDX auth URL — see below)_ | **Yes** |

> **How to get the SFDX Auth URL:**
> ```bash
> sf org display --target-org <your-uat-alias> --verbose
> # Copy the value next to "Sfdx Auth Url"
> ```

#### ADO Variables

| Variable Name | Value | Secret? |
|---------------|-------|---------|
| `ADO_PAT` | _(your Personal Access Token)_ | **Yes** |
| `DEPLOY_PIPELINE_ID` | _(set after Step 3 — pipeline definition ID)_ | No |
| `VARIABLE_GROUP_ID` | _(ID of this variable group — visible in URL after saving)_ | No |

#### CRT Variables

| Variable Name | Value | Secret? |
|---------------|-------|---------|
| `CRT_API_TOKEN` | _(Copado Robotic Testing API token)_ | **Yes** |
| `CRT_JOB_ID` | `115686` (or your job ID) | No |
| `CRT_PROJECT_ID` | `73283` (or your project ID) | No |
| `CRT_ORG_ID` | `43532` (or your org ID) | No |

#### CheckMarx Variables _(optional — skip if not using CheckMarx)_

| Variable Name | Value | Secret? |
|---------------|-------|---------|
| `CX_BASE_URI` | _(CheckMarx AST URL)_ | **Yes** |
| `CX_TENANT` | _(CheckMarx tenant name)_ | **Yes** |
| `CX_CLIENT_ID` | _(CheckMarx client ID)_ | **Yes** |
| `CX_CLIENT_SECRET` | _(CheckMarx client secret)_ | **Yes** |
| `CX_PROJECT_NAME` | _(project name — optional)_ | No |

#### Fortify Variables _(optional — skip if not using Fortify)_

| Variable Name | Value | Secret? |
|---------------|-------|---------|
| `FOD_URL` | _(Fortify on Demand URL)_ | No |
| `FOD_CLIENT_ID` | _(Fortify client ID)_ | **Yes** |
| `FOD_CLIENT_SECRET` | _(Fortify client secret)_ | **Yes** |
| `FOD_APP_NAME` | _(Fortify app name)_ | **Yes** |
| `FOD_RELEASE_NAME` | _(Fortify release name)_ | **Yes** |

4. Click **Save**
5. Note the **Variable Group ID** from the URL: `.../_library/variableGroups?groupId=XX` → set `VARIABLE_GROUP_ID` to `XX`

---

## 4. Step 2 — Create the ADO Environment (Architect Approval Gate)

The deployment stage uses an ADO **Environment** with required approvals to enforce that only Architects can approve a production/UAT deployment.

### 4.1 Create the Environment

1. Go to **Pipelines → Environments → New environment**
2. **Name:** `uat-deployment`
3. **Resource:** None (just the environment shell)
4. Click **Create**

### 4.2 Add Approval Gate

1. Open `uat-deployment` environment
2. Click **⋮ (More actions) → Approvals and checks → +**
3. Select **Approvals**
4. Add approvers:
   - `chorevathi-deloitte`
   - `mukeshranadeloitte`
5. Set **Instructions to approvers:** `Architect approval required. Verify PR has passed all checks before approving deployment.`
6. **Timeout:** 7 days (or your preferred window)
7. Click **Create**

> **Note:** The pipeline also enforces the architect list in code (for main-branch deployments). Both layers of protection are active.

---

## 5. Step 3 — Register the Pipelines in ADO

### 5.1 Register the Main E2E Pipeline

1. Go to **Pipelines → New pipeline**
2. Select **Azure Repos Git** (or your source)
3. Select your repository
4. Select **Existing Azure Pipelines YAML file**
5. Branch: `main` (or `uat`)
6. Path: `/ado-pipelines/e2e-uat-pipeline.yml`
7. Click **Continue → Save** (do not Run yet)
8. **Rename** the pipeline to: `Salesforce UAT E2E Pipeline`
9. Note the **Pipeline ID** from the URL: `.../_build?definitionId=XX` → set `DEPLOY_PIPELINE_ID` to `XX`

### 5.2 Register the Delta Baseline Updater Pipeline

1. Go to **Pipelines → New pipeline**
2. Same steps as above
3. Path: `/ado-pipelines/update-delta-on-uat-push.yml`
4. Click **Continue → Save**
5. **Rename** to: `Update Delta Baseline on UAT Push`

### 5.3 Link the Variable Group to Both Pipelines

For each pipeline:
1. Open the pipeline → **Edit → Variables → Variable groups**
2. Click **Link variable group** → select `salesforce-uat`
3. Save

---

## 6. Step 4 — Configure Branch Policies

Set branch policies on `uat` and `main` to require the pipeline to pass before PRs can be merged.

### 6.1 Add Build Validation Policy (uat branch)

1. Go to **Project Settings → Repos → Branches**
2. Click `...` next to `uat` → **Branch policies**
3. Under **Build validation → + Add build policy**:
   - **Build pipeline:** `Salesforce UAT E2E Pipeline`
   - **Trigger:** Automatic
   - **Policy requirement:** Required
   - **Display name:** `Salesforce PR Validation`
4. Click **Save**

### 6.2 Add the same policy to `main` branch

Repeat the steps above for the `main` branch.

### 6.3 Restrict direct pushes (recommended)

On both `uat` and `main`:
- Enable **Require a minimum number of reviewers:** 1
- Enable **Check for linked work items** (optional)
- Enable **Block direct pushes** to ensure all changes go through PRs

> **Note:** The `update-delta-on-uat-push.yml` pipeline handles the case where direct pushes to `uat` are permitted by updating `DELTA_FROM_COMMIT` automatically.

---

## 7. Step 5 — Set the Delta Baseline (First-Time Only)

`DELTA_FROM_COMMIT` must point to the last commit that was deployed to UAT. On first setup, set it to the current `uat` branch tip.

### 7.1 Get the current UAT branch tip SHA

```bash
git checkout uat
git rev-parse HEAD
# Example output: a1b2c3d4e5f6...
```

### 7.2 Update the variable

1. Go to **Pipelines → Library → salesforce-uat**
2. Find `DELTA_FROM_COMMIT`
3. Set the value to the SHA from Step 7.1
4. Click **Save**

> After this, every deployment automatically updates `DELTA_FROM_COMMIT` to the latest deployed SHA. Every push to `uat` (including direct pushes) also updates it via the delta baseline updater pipeline.

---

## 8. Pipeline Job Reference

### Stage 1: PR Validation

| Job | What it does | Condition |
|-----|-------------|-----------|
| **Evaluate Scanner Availability** | Checks which security scanners are configured based on available secrets | Always |
| **Salesforce PR validation** | Full SF check-only deploy: delta build → validate → coverage → SCA → reviewer notify | PR events only |
| **CheckMarx AST Scan** | SAST scan using CheckMarx AST | Only if `CX_CLIENT_SECRET` is set |
| **Fortify on Demand Scan** | SAST/DAST scan using Fortify on Demand | Only if `FOD_CLIENT_SECRET` is set |

### Stage 2: Deployment

| Job | What it does | Condition |
|-----|-------------|-----------|
| **Approval + Merge Gate** | Waits for architect approval via ADO Environment gate | Manual trigger / post-PR |
| **Deploy merged commit** | Delta deploy to UAT org (`NoTestRun` — tests already ran in validation) | After gate approval |
| **Trigger CRT Tests** | Triggers Copado Robotic Testing job and polls for result | After deployment succeeds |

---

## 9. How the Pipeline Works — End to End

### PR Validation Flow

```
Developer opens PR (feature → uat or uat → main)
        │
        ▼
[Pipeline auto-triggers via branch policy]
        │
        ├──▶ Request reviewers (ss10del, chorevathi-deloitte — excluding PR author)
        ├──▶ Checkout full git history
        ├──▶ Authenticate SF org (SFDX Auth URL)
        ├──▶ Build delta: only changed components since last deploy
        ├──▶ Check-only deploy to UAT org (--dry-run)
        │       └── Poll for completion, show component/test table
        ├──▶ Check Apex test coverage (threshold: COVERAGE_THRESHOLD %)
        ├──▶ Run Salesforce Code Analyzer (sf scanner run)
        ├──▶ Evaluate violations against sf-scanner-waivers.csv (from main branch)
        ├──▶ Post SCA governance report as PR comment
        └──▶ Notify reviewers: "✅ All checks passed — ready for review"
```

### Test Class Resolution

The pipeline resolves which test classes to run in this priority order:

1. **PR description** — Add `Tests: ClassName1, ClassName2` line in the PR body
2. **Inferred by convention** — classes named `*Test`, `*Tests`, `*TestClass` matching changed classes
3. **@isTest annotation** — scans changed `.cls` files for the annotation
4. **No Apex changed** — skips test execution (`NoTestRun`)

### Deployment Flow

```
Architect approves PR in ADO (approval gate on uat-deployment environment)
        │
        ▼
[Deployment stage triggers]
        │
        ├──▶ Architect gate check (validates approver is in ARCHITECTS list for main)
        ├──▶ Rebuild delta: DELTA_FROM_COMMIT → HEAD
        ├──▶ Deploy to UAT org (--test-level NoTestRun — tests already validated)
        │       └── Poll for completion
        ├──▶ Update DELTA_FROM_COMMIT → deployed commit SHA
        └──▶ Trigger CRT automated tests → poll → post summary
```

### SCA Enforcement Modes

Control via `SCA_ENFORCEMENT_MODE` variable:

| Mode | Behavior |
|------|---------|
| `enforce` | ❌ Fails if expired waivers or unwaived violations found |
| `warn` | ⚠️ Reports violations as warnings; pipeline continues |
| `off` | Skips all SCA steps entirely |

---

## 10. SCA Waivers

Violations can be waived by adding entries to `.github/sf-scanner-waivers.csv`.

> **Important:** The pipeline always reads waivers from the `main` branch — changes in feature branches are ignored. Only commits to `main` take effect.

### Waiver File Format

```csv
Component,Rule,Description,ExpiryDate,Status
force-app/main/default/classes/CoverageDemoService.cls,ApexDoc,Missing ApexDoc comment,2025-09-09,ACTIVE
```

| Column | Description |
|--------|-------------|
| `Component` | File path (partial match) or leave blank to match all files |
| `Rule` | Rule name from the scanner (e.g. `ApexDoc`, `AvoidGlobalModifier`) |
| `Description` | Human-readable reason for the waiver |
| `ExpiryDate` | `YYYY-MM-DD` — waiver expires after this date |
| `Status` | `ACTIVE` = active waiver; `REVOKED` = waiver removed |

### Waiver States Reported by Pipeline

| State | Meaning |
|-------|---------|
| ✅ Waived (active) | Valid waiver — violation suppressed |
| ⏰ Expiring ≤30 days | Active but expiring soon — action needed |
| ❌ Expired | Waiver date passed — **fails in enforce mode** |
| ⚠️ Unwaived | No matching waiver — **fails in enforce mode** |

---

## 11. Troubleshooting

### Pipeline doesn't trigger on PR

**Check:**
- Branch policy is set to **Required** on the target branch (`uat` / `main`)
- PR paths include `force-app/**` — PRs that only change docs won't trigger

---

### `DELTA_FROM_COMMIT` not found or empty

**Fix:** Follow [Step 5](#7-step-5--set-the-delta-baseline-first-time-only) to set the initial baseline SHA.

---

### SF authentication fails

**Check:**
- `CRT_UAT_AUTHURL` secret in the variable group is not empty
- The SFDX auth URL hasn't expired (connected app session)
- Re-generate: `sf org display --target-org <alias> --verbose`

---

### Check-only deploy fails with component errors

**Check:**
- The changed components are valid in the UAT org's API version
- Run locally: `sf project deploy start --dry-run --manifest package/package.xml --target-org <alias>`

---

### Coverage check fails

**Check:**
- Add `Tests: ClassName` to your PR description
- Ensure the test class covers the changed production class
- Coverage threshold is configurable via `COVERAGE_THRESHOLD` variable (default: 85%)

---

### Architect gate fails (wrong approver)

The pipeline enforces that only architects can approve main-branch deployments.

**To add an architect:** Edit the `ARCHITECTS` array in `ado-pipelines/e2e-uat-pipeline.yml`:
```yaml
ARCHITECTS=("chorevathi-deloitte" "mukeshranadeloitte" "new-architect-username")
```
Also add them as an approver in the `uat-deployment` ADO Environment.

---

### ADO_PAT permissions error

**Check the PAT has these scopes:**
- Code: `Read`
- Build: `Read & Execute`
- Variable Groups: `Read & Manage`
- Pull Request Threads: `Read & Write`
- Identity: `Read`

---

### CRT job not triggering

**Check:**
- `CRT_API_TOKEN` secret is set and not expired
- `CRT_JOB_ID`, `CRT_PROJECT_ID`, `CRT_ORG_ID` match your Copado project settings
- The UAT deployment succeeded before this job runs

---

### DELTA_FROM_COMMIT not updating after deployment

The pipeline updates this variable via ADO REST API using `ADO_PAT`. If it fails:

1. Check `ADO_PAT` has **Variable Groups: Read & Manage** scope
2. Check `DEPLOY_PIPELINE_ID` is set to the correct pipeline definition ID
3. Fallback: manually update `DELTA_FROM_COMMIT` in the variable group to `git rev-parse HEAD` on UAT branch

---

## Quick Start Checklist

```
□ 1. Create variable group 'salesforce-uat' with all required variables
□ 2. Create ADO Environment 'uat-deployment' with architect approvers
□ 3. Register e2e-uat-pipeline.yml as pipeline 'Salesforce UAT E2E Pipeline'
□ 4. Register update-delta-on-uat-push.yml as pipeline 'Update Delta Baseline on UAT Push'
□ 5. Link variable group 'salesforce-uat' to both pipelines
□ 6. Note DEPLOY_PIPELINE_ID and VARIABLE_GROUP_ID — update in variable group
□ 7. Add branch policy on 'uat' and 'main' — require 'Salesforce PR Validation' to pass
□ 8. Set DELTA_FROM_COMMIT to current UAT branch tip SHA
□ 9. Open a test PR to uat branch and verify pipeline triggers
□ 10. Verify SCA waiver file exists at .github/sf-scanner-waivers.csv on main branch
```
