# Salesforce CI/CD Pipeline — Client Assessment Questionnaire

> **Purpose:** Understand your current CI/CD maturity and identify how the UAT End-to-End Pipeline can improve your delivery process.
>
> **Instructions:** For each item, mark your current status:
> - ✅ **Already have it** — fully implemented
> - ⚠️ **Partially** — in place but incomplete or inconsistent
> - ❌ **Not in place** — not implemented
> - ❓ **Unsure** — need to investigate

---

## Section 1 — Source Control & Branching

| # | Question | Status | Notes / Details |
|---|----------|--------|-----------------|
| 1.1 | Do you use Git-based source control (GitHub / GitLab / Bitbucket)? | | |
| 1.2 | Do you have a dedicated UAT/integration branch separate from main? | | |
| 1.3 | Are all Salesforce metadata changes committed via source control (not direct org deployment)? | | |
| 1.4 | Do you follow a Pull Request (PR) / Merge Request process before deploying? | | |
| 1.5 | Do you have branch protection rules (e.g. require PR reviews before merge)? | | |

**How this pipeline helps:** Enforces a PR-first workflow with branch protection, automatically validates every PR before it can be merged, and prevents direct deploys to UAT by requiring all changes to flow through the pipeline.

---

## Section 2 — PR Validation & Delta Deployment

| # | Question | Status | Notes / Details |
|---|----------|--------|-----------------|
| 2.1 | Do you validate changes against the target org **before** merging? | | |
| 2.2 | Do you deploy only the **delta** (changed components) rather than the full org metadata? | | |
| 2.3 | Do you track which **Apex test classes** to run per PR (specified in PR or auto-inferred)? | | |
| 2.4 | Do you handle **destructive changes** (deleted components) in your pipeline? | | |
| 2.5 | Do you receive **live deployment progress** during CI runs (component count, errors, status)? | | |
| 2.6 | Do you get a **per-component breakdown** (created / updated / deleted) in your pipeline logs? | | |
| 2.7 | Are reviewers **automatically requested** and notified when a PR is opened? | | |

**How this pipeline helps:** Uses `sfdx-git-delta` to compute the exact diff between the PR branch and the UAT tip — only changed components are validated/deployed. Test classes are extracted from the PR description or automatically inferred from naming conventions (`*Test`, `*Tests`, `*TestClass`). Live progress is streamed every 15 seconds with a formatted table showing component and test counts.

---

## Section 3 — Test Coverage & Apex Testing

| # | Question | Status | Notes / Details |
|---|----------|--------|-----------------|
| 3.1 | Is Apex test coverage enforced **automatically** in your pipeline? | | |
| 3.2 | What is your current **minimum Apex coverage threshold**? | | ____% |
| 3.3 | Do you receive **per-class coverage breakdowns** in your pipeline output? | | |
| 3.4 | Are test failures surfaced clearly with **class name + method + error message**? | | |
| 3.5 | Are coverage warnings (classes below threshold) reported separately from failures? | | |

**How this pipeline helps:** Enforces a configurable coverage threshold (default 85%, set via `vars.COVERAGE_THRESHOLD`). Per-class coverage is printed in a formatted report. Test failures include full class name, method name, and error message. Coverage warnings are distinguished from component failures.

---

## Section 4 — Code Quality (Salesforce Code Analyzer / SAST)

| # | Question | Status | Notes / Details |
|---|----------|--------|-----------------|
| 4.1 | Do you run **Salesforce Code Analyzer** (SF CLI scanner) on PRs? | | |
| 4.2 | Does your scanner target only **changed files** (not the entire repo on every PR)? | | |
| 4.3 | Does your pipeline **post scanner results as a PR comment** for developer visibility? | | |
| 4.4 | Do you have a **waiver / exemption mechanism** for known violations? | | |
| 4.5 | Do waivers **auto-expire** after a set date (forcing eventual remediation)? | | |
| 4.6 | Can you waive violations at different levels? (specific file / all files for a rule / all rules for a component) | | |
| 4.7 | Are waiver files **protected** so only authorised staff (Tech Lead / DevOps) can update them on `main`? | | |
| 4.8 | Do you scan **LWC / JavaScript** components in addition to Apex? | | |
| 4.9 | Can the scanner be **toggled off** during initial project phases without editing the workflow? | | |

**How this pipeline helps:** Scans only changed `.cls`, `.trigger`, `.js`, `.html`, `.css` files per PR. Results are posted as a PR comment with a colour-coded governance table (✅ Waived / ⏰ Expiring / ❌ Expired / ⚠️ Unwaived). Waivers are stored in `.github/sf-scanner-waivers.csv` on `main` only — developers cannot bypass them via PR branches. Enforcement is controlled by `vars.SCA_ENFORCEMENT_MODE` (`enforce` / `warn` / `off`).

---

## Section 5 — Dependency Security (npm SCA)

| # | Question | Status | Notes / Details |
|---|----------|--------|-----------------|
| 5.1 | Do you run **npm audit** or equivalent dependency vulnerability scanning? | | |
| 5.2 | Do you block the pipeline on **high/critical** npm vulnerabilities? | | |
| 5.3 | Do you have a **waiver mechanism** for known npm vulnerabilities with expiry dates? | | |
| 5.4 | Do npm audit results survive the pipeline even if `package.json` doesn't exist in the repo? | | |

**How this pipeline helps:** Runs `npm audit --json` on every PR. High/critical vulnerabilities are matched against `.github/sca-waivers.json`. Active waivers (with future expiry) pass; expired waivers fail the pipeline. If no `package.json` exists, a standard Salesforce one is auto-created so `npm audit` can run without error.

---

## Section 6 — Advanced SAST (CheckMarx / Fortify)

| # | Question | Status | Notes / Details |
|---|----------|--------|-----------------|
| 6.1 | Do you use **CheckMarx AST** for SAST scanning? | | |
| 6.2 | Do you use **Fortify on Demand** for SAST scanning? | | |
| 6.3 | Do you perform **DAST** (Dynamic Application Security Testing)? | | |
| 6.4 | Are SAST results published to **GitHub Code Scanning / Security tab**? | | |
| 6.5 | Do SAST scans run **in parallel** with other pipeline jobs (not blocking deployments)? | | |
| 6.6 | Can individual scanners be **enabled/disabled** without editing the YAML? | | |

**How this pipeline helps:** CheckMarx (Job 5) and Fortify (Job 6) run in parallel with PR validation — they do not block the deploy path. Each scanner is enabled automatically when its corresponding secret is present (`CX_CLIENT_SECRET` / `FOD_CLIENT_SECRET`). SARIF reports are uploaded to GitHub Code Scanning. A `scanner` input on `workflow_dispatch` allows targeting a specific scanner or both.

---

## Section 7 — Deployment Approval & Merge Gate

| # | Question | Status | Notes / Details |
|---|----------|--------|-----------------|
| 7.1 | Does your pipeline require **at least one PR approval** before deployment? | | |
| 7.2 | Does your pipeline check that the approval is for the **latest commit** (not a stale review)? | | |
| 7.3 | Does your pipeline verify **all required checks passed** before allowing merge? | | |
| 7.4 | Is the PR **automatically merged** once approved and all checks pass? | | |
| 7.5 | Is there a record of **who approved** and **who triggered** each deployment? | | |

**How this pipeline helps:** The Approval + Merge Gate (Job 7) triggers on `pull_request_review` approval. It validates the approval is for the latest commit SHA, checks that Salesforce Validation, SCA/SAST Stage, Automated Hard Gates (and optional CheckMarx/Fortify) all have a successful run, then auto-merges via GitHub API. The approver and PR raiser are recorded in the CRT summary comment.

---

## Section 8 — Post-Merge Deployment

| # | Question | Status | Notes / Details |
|---|----------|--------|-----------------|
| 8.1 | Does your pipeline automatically **deploy to UAT** after PR is merged? | | |
| 8.2 | Do you maintain a **deployment history** (what was deployed, when, by whom)? | | |
| 8.3 | Are deployment packages (package.xml + components.zip) **stored as artefacts**? | | |
| 8.4 | Is a **baseline commit SHA** automatically tracked for the next delta calculation? | | |
| 8.5 | Are deployment packages **committed to a dedicated branch** for long-term audit? | | |

**How this pipeline helps:** After merge, Job 8 checks out the merge commit, rebuilds the delta using the same base as validation (HEAD^1), and deploys. A deployment package (package.xml, destructiveChanges.xml, components.zip, deployment-info.json) is uploaded as a GitHub Artefact (90-day retention) and committed to the `pr_packages` orphan branch. `DELTA_FROM_COMMIT` is automatically updated via GitHub API for the next PR's baseline.

---

## Section 9 — Rollback

| # | Question | Status | Notes / Details |
|---|----------|--------|-----------------|
| 9.1 | Do you have a documented **rollback procedure** for failed deployments? | | |
| 9.2 | Can rollback be triggered with a **single action** (e.g. one-click workflow trigger)? | | |
| 9.3 | Does rollback correctly handle **new metadata** introduced by the PR (destructive delete)? | | |
| 9.4 | Are rollback actions **logged and commented** on the original PR? | | |
| 9.5 | What is your current average time to rollback a bad deployment? | | ____mins |

**How this pipeline helps:** Rollback (Job 11) is triggered via `workflow_dispatch` with `action=rollback` and a `rollback_commit_sha`. It uses `sfdx-git-delta` in reverse: components added by the PR are deleted (pre-destructive), components previously deleted are re-deployed. A result comment is posted to the original PR with from/to SHA, status, and a link to the Actions run.

---

## Section 10 — Automated Smoke / Regression Testing

| # | Question | Status | Notes / Details |
|---|----------|--------|-----------------|
| 10.1 | Do you run automated **smoke or regression tests** after every UAT deployment? | | |
| 10.2 | Do you use **Copado Robotic Testing (CRT)** or equivalent test automation tool? | | |
| 10.3 | Are test results **summarised and posted** back to the PR? | | |
| 10.4 | Does a failed smoke test result in a **visible notification** to the team? | | |
| 10.5 | Is a **link to the test dashboard** included in the pipeline summary? | | |

**How this pipeline helps:** After deployment, Job 10 triggers a CRT build via GraphQL API, polls for completion, and posts a result summary box to the PR:
```
╔══════════════════════════════════════════╗
║        CRT Job Execution Summary         ║
╠══════════════════════════════════════════╣
  PR Number       : #<n>
  PR Raiser       : <username>
  PR Approver     : <username>
  Test Build ID   : <id>
  Test Result     : PASSED / FAILED
╚══════════════════════════════════════════╝
```
A link to the CRT dashboard is added to the GitHub Step Summary.

---

## Section 11 — Observability & Governance

| # | Question | Status | Notes / Details |
|---|----------|--------|-----------------|
| 11.1 | Do you have a **single pipeline** covering PR validation → approval → deploy → test? | | |
| 11.2 | Are all pipeline artefacts (reports, logs, packages) **retained** for audit purposes? | | |
| 11.3 | Can pipeline behaviour be configured via **repository variables** without editing YAML? | | |
| 11.4 | Can you **bypass SCA** during initial project setup without removing scanner steps? | | |
| 11.5 | Are concurrent pipeline runs **cancelled automatically** when a new commit is pushed? | | |
| 11.6 | Do you have **destructive change reminders** posted to PRs automatically? | | |

**How this pipeline helps:** All configurable values are exposed as `vars.*` repository variables (no YAML edits needed). `SCA_ENFORCEMENT_MODE=off` bypasses all scanner steps. Concurrency groups cancel superseded runs automatically. Artefacts are retained for 7–90 days depending on type. Destructive changes trigger an automatic PR comment reminding reviewers to confirm data backup.

---

## Section 12 — Current Pain Points

| # | Question | Your Answer |
|---|----------|-------------|
| 12.1 | What is the biggest bottleneck in your current CI/CD pipeline? | |
| 12.2 | How long does a typical PR-to-UAT-deployment cycle take today? | |
| 12.3 | How often do failed deployments require manual intervention? | |
| 12.4 | Do developers have clear visibility of **why** a pipeline failed? | |
| 12.5 | Are there compliance/security scan requirements you currently cannot meet? | |
| 12.6 | Which Salesforce metadata types cause the most deployment issues? | |
| 12.7 | Is your current coverage threshold enforced automatically or manually reviewed? | |
| 12.8 | How do you currently handle emergency rollbacks? | |

---

## Scoring Guide

Count the number of ✅ responses across Sections 1–11 and use the table below to gauge maturity:

| Score | Maturity Level | Recommendation |
|-------|----------------|----------------|
| 0–30% ✅ | Manual / ad-hoc | Pipeline provides **immediate high value** — automates most of the delivery process from scratch |
| 31–60% ✅ | Partial automation | Pipeline **fills critical gaps** — delta deploy, waivers, auto-merge, rollback |
| 61–80% ✅ | Mature CI/CD | Pipeline **enhances governance & security** — SCA enforcement, expiry-based waivers, CRT integration |
| 81–100% ✅ | Advanced | Pipeline offers **fine-tuning** — custom waiver levels, parallel SAST, audit trail, advanced rollback |

---

## Pipeline Summary — What This Pipeline Delivers

| Capability | Detail |
|------------|--------|
| **Delta deployment** | Only changed components deployed — faster, safer |
| **Auto test class inference** | Named `*Test` / `*Tests` classes found automatically |
| **PR validation** | Check-only deploy validates before merge |
| **Apex coverage enforcement** | Configurable threshold (default 85%) |
| **Salesforce Code Analyzer** | Scans only changed files; results as PR comment |
| **SCA waiver system** | Expiry-based with 4 waiver levels (specific / global rule / global component / global all) |
| **npm dependency audit** | High/critical vulnerabilities checked with waiver support |
| **CheckMarx SAST** | Optional; enabled by secret presence |
| **Fortify SAST + DAST** | Optional; enabled by secret presence |
| **Auto reviewer request** | Designated reviewers requested and notified on PR open |
| **Approval + merge gate** | Verifies freshness of approval + all checks before auto-merge |
| **Post-merge deployment** | Deploys merge commit to UAT; streams live progress |
| **Deployment artefacts** | package.xml, components.zip, deployment-info.json — 90-day retention |
| **Rollback** | One-click via `workflow_dispatch`; handles new metadata correctly |
| **CRT smoke tests** | Auto-triggered after deploy; result posted as PR comment |
| **Audit trail** | PR raiser, approver, deployed SHA, run URL all recorded |

---

*Document generated from `e2e-uat-pipeline.yml` — UAT End-to-End Pipeline*
