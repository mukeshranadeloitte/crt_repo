# UAT End-to-End Pipeline — Overview

This document describes the CI/CD pipeline defined in `.github/workflows/e2e-uat-pipeline.yml`.

---

## Flow Diagram

```
pull_request (force-app/**)
        │
        ├──► [1] setup
        │           │ (outputs: run-checkmarx, run-fortify)
        │
        ├──► [2] salesforce-validation
        │           │
        │     ┌─────┴──────────────────────┐
        │     ▼                            ▼
        │  [3] sca-sast-stage    [4] automated-governance
        │     │                            │
        │  ┌──┴───────────┐               ▼
        │  ▼              ▼        [7] manual-validation
        │  [5]            [6]           (ReleaseGate)
        │  checkmarx-sast fortify-sast-dast
        │
pull_request_review (APPROVED)
        │
        ├──► [8] approval-merge-gate
        │           │
        │           ▼
        │    [9] deploy-after-merge
        │           │
        │           ▼
        │    [10] trigger-crt-tests
```

---

## Job Summary

| # | Job | Trigger | Purpose |
|---|-----|---------|---------|
| 1 | `setup` | PR / dispatch | Evaluate which security scanners to run |
| 2 | `salesforce-validation` | PR | Check-only validate delta + Salesforce Code Analyzer |
| 3 | `sca-sast-stage` | PR / dispatch | `npm audit` dependency vulnerability gate |
| 4 | `automated-governance` | PR | Apex coverage (75%) + destructive-changes guard + Code Analyzer |
| 5 | `checkmarx-sast` | PR / dispatch | CheckMarx AST SAST scan (conditional on secret) |
| 6 | `fortify-sast-dast` | PR / dispatch | Fortify SAST + optional DAST (conditional on secret) |
| 7 | `manual-validation` | PR | Human approval gate via `ReleaseGate` environment |
| 8 | `approval-merge-gate` | PR review APPROVED | Stale-approval guard + required-checks gate + auto-merge |
| 9 | `deploy-after-merge` | PR review APPROVED | Real deploy from merge commit to UAT org |
| 10 | `trigger-crt-tests` | PR review APPROVED | Trigger Copado Robotic Testing job |

---

## Trigger Events

| Event | Condition | Jobs Activated |
|-------|-----------|----------------|
| `pull_request` | Opened/updated targeting `uat` or `UberDemo`; files under `force-app/**` | 1–7 |
| `pull_request_review` | Review submitted with state `APPROVED` | 8–10 |
| `workflow_dispatch` | Manual run; optional `scanner` input (`checkmarx / fortify / all`) | 1, 3, 5, 6 |

---

## Security Gates

| Gate | Tool | Condition |
|------|------|-----------|
| Dependency SCA | `npm audit --audit-level=high` | Always on PR |
| SAST | CheckMarx AST (`sast + kics`) | `CX_CLIENT_SECRET` set + scanner includes `checkmarx` |
| SAST | Fortify FoD | `FOD_CLIENT_SECRET` set + scanner includes `fortify` |
| DAST | Fortify FoD | `FOD_DAST_SCAN_URL` secret set |
| Code coverage | Salesforce platform (75% min per class) | Any Apex change |
| Governance coverage | Apex test run in UAT org | Always on PR |

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
