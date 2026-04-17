# UAT End-to-End Pipeline — Overview

This document describes the CI/CD pipeline defined in `.github/workflows/e2e-uat-pipeline.yml`.

---

## Flow Diagram

```
pull_request (force-app/**)
        │
        └──► [1] setup
                   │ (outputs: run-checkmarx, run-fortify)
                   │
         ┌─────────┼──────────────────────────────────────┐
         ▼         ▼            ▼                  ▼       │
   [2] salesforce  [3] sca-sast [5] checkmarx-sast [6] fortify-sast-dast
       -validation     -stage       (if CX secret)    (if FOD secret)
         │                │
         ▼                │  (reviewer auto-request + notify on every PR event)
   [4] automated-         │
       governance         │
         │                │
         └────────┬────────┘
                  ▼
           PR reviewer approves → pull_request_review event fires

pull_request_review (APPROVED)
        │
        └──► [7] approval-merge-gate
                        │
                        ▼
                [8] deploy-after-merge
                        │
                        ▼
                [9] trigger-crt-tests

workflow_dispatch (action=rollback)
        │
        └──► [10] rollback
```

---

## Job Summary

| # | Job | Trigger | Depends On | Purpose |
|---|-----|---------|------------|---------|
| 1 | `setup` | PR / dispatch | — | Evaluate which security scanners to run |
| 2 | `salesforce-validation` | PR | `setup` | Request reviewers, check-only validate delta + Salesforce Code Analyzer |
| 3 | `sca-sast-stage` | PR / dispatch | `setup` | `npm audit` dependency vulnerability gate |
| 4 | `automated-governance` | PR | `salesforce-validation` | Apex coverage (≥ COVERAGE_THRESHOLD, default 85%) + destructive-changes guard |
| 5 | `checkmarx-sast` | PR / dispatch | `setup` | CheckMarx AST SAST scan (conditional on `CX_CLIENT_SECRET`) |
| 6 | `fortify-sast-dast` | PR / dispatch | `setup` | Fortify SAST + optional DAST (conditional on `FOD_CLIENT_SECRET`) |
| 7 | `approval-merge-gate` | PR review APPROVED | — | Stale-approval guard + required-checks gate + auto-merge |
| 8 | `deploy-after-merge` | PR review APPROVED | `approval-merge-gate` | Real deploy from merge commit to UAT org |
| 9 | `trigger-crt-tests` | PR review APPROVED | `deploy-after-merge` | Trigger Copado Robotic Testing job |
| 10 | `rollback` | `workflow_dispatch` (action=rollback) | — | Revert last deployment via reverse delta |

---

## Trigger Events

| Event | Condition | Jobs Activated |
|-------|-----------|----------------|
| `pull_request` | Opened/updated/synchronised targeting `uat`; files under `force-app/**` or workflow/waivers changed | 1–6 |
| `pull_request_review` | Review submitted with state `APPROVED` | 7–9 |
| `workflow_dispatch` | Manual run; `scanner` input (`checkmarx / fortify / all`), `action` input (`deploy / rollback`) | 1, 3, 5, 6 (or 10 for rollback) |

---

## Security Gates

| Gate | Tool | Condition |
|------|------|-----------|
| Dependency SCA | `npm audit --audit-level=high` | Always on PR (Job 3) |
| SF Code Analyzer | `sf scanner run` + waiver check | PR with delta (Job 2); `SCA_ENFORCEMENT_MODE` controls failure behaviour |
| SAST | CheckMarx AST (`sast + kics`) | `CX_CLIENT_SECRET` set + scanner includes `checkmarx` (Job 5) |
| SAST | Fortify FoD | `FOD_CLIENT_SECRET` set + scanner includes `fortify` (Job 6) |
| DAST | Fortify FoD | `FOD_DAST_SCAN_URL` secret set (Job 6) |
| Apex code coverage | Salesforce platform | Any Apex change; threshold = `COVERAGE_THRESHOLD` (default 85%) |
| Hard gates | Apex test run in UAT org | PR with delta (Job 4) |

---

## Approval & Auto-Merge Logic

When a PR review is submitted with state **APPROVED**:

1. **Stale-approval check** — verifies `review.commit_id == pull_request.head.sha`
2. **Required checks gate** — queries all check-runs for the head SHA; a check passes if **any** `completed + success` entry exists (not just the latest — avoids false failures from `skipped` entries created when `pull_request_review` fires)
3. **Auto-merge** — creates a merge commit via GitHub API
4. **Deploy** — checks out the merge commit SHA and runs `sf project deploy start`
5. **CRT trigger** — fires the Copado Robotic Testing job

---

## Related Docs

- [Setup & Configuration](./pipeline-setup.md)
- [Manual Runbook](./manual_runbook.md)
- [Troubleshooting](./troubleshooting.md)
