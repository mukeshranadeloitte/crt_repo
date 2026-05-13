# UAT End-to-End Pipeline — Flow Diagram

## Overview

The `UAT End-to-End Pipeline` automates the full lifecycle of a Salesforce change from PR creation through security scanning, approval, deployment to UAT, and robotic test execution.

### Triggers

| Event | What it does |
|-------|-------------|
| `pull_request` → `uat` | Runs validation + security scans + reviewer notification |
| `pull_request_review` (approved) | Merges PR + deploys + triggers CRT tests |
| `workflow_dispatch` (deploy) | Manual security scan trigger |

---

## Full Pipeline Flow

```mermaid
flowchart TD
    START([🚀 PR opened / pushed to UAT branch]) --> SETUP
    START --> SF_VAL

    subgraph JOB1["JOB 1 — Evaluate Scanner Availability"]
        SETUP["⚙️ setup\nCheck if CX_CLIENT_SECRET / FOD_CLIENT_SECRET exist\nOutput: run-checkmarx, run-fortify flags"]
    end

    SETUP --> CX
    SETUP --> FORTIFY

    subgraph JOB2["JOB 2 — Salesforce PR Validation"]
        SF_VAL["🔵 salesforce-validation
        1. Request reviewers: ss10del, chorevathi-deloitte
        2. Checkout + install SF CLI
        3. Authenticate UAT org
        4. Extract test classes from PR description
        5. Build delta (sfdx-git-delta: base → head)
        6. Validate deploy to UAT org (check-only + async polling)
        7. Check Apex test coverage >= threshold
        8. Fetch SCA waivers from main branch (tamper-proof)
        9. Run Salesforce Code Analyzer on changed files
        10. Compare violations against waivers (expired = FAIL)
        11. Post SCA governance report as PR comment
        Output: has_delta"]
    end

    subgraph JOB3["JOB 3 — CheckMarx SAST (if CX secret present)"]
        CX["🔴 checkmarx-sast
        Checkmarx/ast-github-action
        SAST + KICS scan → SARIF
        Upload to GitHub Code Scanning"]
    end

    subgraph JOB4["JOB 4 — Fortify FoD SAST + DAST (if FOD secret present)"]
        FORTIFY["🟠 fortify-sast-dast
        fortify/github-action SAST → SARIF
        Optional DAST scan via fcli if FOD_DAST_SCAN_URL set
        Upload to GitHub Code Scanning"]
    end

    SF_VAL --> FAN_IN
    CX --> FAN_IN
    FORTIFY --> FAN_IN

    FAN_IN(("All pass?"))
    FAN_IN -->|"❌ Any job failed"| PIPELINE_FAIL(["❌ Pipeline fails\nNo merge or deploy"])
    FAN_IN -->|"✅ All pass"| REVIEW_TRIGGER(["👍 Reviewer approves PR\npull_request_review event"])

    REVIEW_TRIGGER --> MERGE_GATE

    subgraph JOB5["JOB 5 — Approval + Merge Gate"]
        MERGE_GATE["🔒 approval-merge-gate
        1. Verify approval is for latest commit SHA (not stale)
        2. Confirm all required checks passed on this SHA
        3. Architect gate — main branch only (architect list enforced)
        4. Merge PR via GitHub API (merge commit)
        Output: merge_sha, head_sha, base_sha, pr_number"]
    end

    MERGE_GATE -->|"✅ Merged"| DEPLOY

    subgraph JOB6["JOB 6 — Deploy After Merge"]
        DEPLOY["🚀 deploy-after-merge
        1. Checkout merge commit (merge_sha from gate)
        2. Install SF CLI
        3. Authenticate org
        4. Install sfdx-git-delta
        5. Build delta (base_sha → merge commit HEAD)
        6. Display & upload delta artifacts
        7. Prepare deploy manifests (check package.xml / destructiveChanges.xml)
        8. Deploy with NoTestRun (tests already run in PR validation)
        9. Update DELTA_FROM_COMMIT (git rev-parse HEAD = merge commit)"]
    end

    DEPLOY -->|"✅ Deployed"| CRT

    subgraph JOB7["JOB 7 — CRT Smoke Tests"]
        CRT["🤖 trigger-crt-tests
        1. Trigger Copado Robotic Testing job via GraphQL API
        2. Poll build status every 30s until pass/fail/timeout
        3. CRT Job Summary: print console box AND write GitHub Step Summary
        4. Post deployment comment to PR"]
    end
```

---

## SCA Enforcement Modes

The `SCA_ENFORCEMENT_MODE` repository variable controls how Code Analyzer violations are handled:

```mermaid
flowchart LR
    MODE{SCA_ENFORCEMENT_MODE} -->|off| SKIP["⏭️ All SCA steps skipped\nbypass for initial project phase"]
    MODE -->|warn| WARN["⚠️ Violations logged as warnings\nNothing fails — informational only"]
    MODE -->|enforce| ENFORCE["❌ Expired waivers = pipeline FAIL\nUnwaived violations = warning only\ndefault"]
```

---

## Waiver Governance Flow

```mermaid
flowchart TD
    V["Developer identifies SF Code Analyzer violation\nthat cannot be fixed immediately"] --> PR_WAIVER
    PR_WAIVER["Raise PR adding row to\n.github/sf-scanner-waivers.csv on main branch"] --> REVIEW
    REVIEW["Tech Lead reviews:\n• Expiry date <= 30 days from today\n• Business justification present\n• Jira/ticket reference included"] --> MERGE_W
    MERGE_W["Merge waiver PR to main"] --> PIPELINE
    PIPELINE["Pipeline fetches waivers from main\ntamper-proof — PR branch waivers are ignored"] --> CHECK
    CHECK{Waiver match\nand expiry?}
    CHECK -->|"ACTIVE + not expired"| WAIVED["✅ WAIVED — pipeline continues"]
    CHECK -->|"Expiring within 30 days"| SOON["⏰ Warning — expiring soon"]
    CHECK -->|"Past expiry date"| EXPIRED["❌ FAIL — fix violation or renew waiver"]
    CHECK -->|"No waiver found"| VIOL["⚠️ VIOLATION — warning only (in enforce mode)"]
```

---

## Delta Calculation

```mermaid
flowchart LR
    subgraph Validation["PR Validation — Job 2"]
        BASE["github.event.pull_request.base.sha\nUAT branch tip when PR opened"] -->|"delta FROM"| HEAD1["github.event.pull_request.head.sha\nLatest PR commit"]
    end

    subgraph Deploy["Deploy After Merge — Job 6"]
        PARENT["base_sha (PR base / UAT tip before merge)\nfrom approval-merge-gate outputs"] -->|"delta FROM"| MERGED["merge_sha (merge commit)\nchecked out in deploy job"]
    end

    Validation -.->|"Same set of components"| Deploy
```

> This ensures exactly the same components that were validated are deployed — no surprises.

---

## Job Execution Matrix

| # | Job Name | Event Trigger | Depends On | Key Condition |
|---|----------|--------------|------------|---------------|
| 1 | Evaluate Scanner Availability | PR, dispatch | — | Not pull_request_review |
| 2 | Salesforce PR Validation | PR | *(none)* | pull_request event |
| 3 | CheckMarx AST Scan | PR, dispatch | setup | run-checkmarx=true (CX secret present, parallel) |
| 4 | Fortify FoD Scan | PR, dispatch | setup | run-fortify=true (FOD secret present, parallel) |
| 5 | Approval + Merge Gate | PR review | — | pull_request_review + approved |
| 6 | Deploy After Merge | PR review | approval-merge-gate | merged=true |
| 7 | Trigger CRT Tests | PR review | deploy-after-merge | deploy result=success |

---

## Key Secrets & Variables

| Name | Type | Purpose |
|------|------|---------|
| `CRT_UAT_AUTHURL` | Secret | Salesforce SFDX auth URL for UAT org |
| `GH_PAT` | Secret | Fine-grained PAT to update `DELTA_FROM_COMMIT` variable |
| `CRT_API_TOKEN` | Secret | Copado Robotic Testing API token |
| `CX_CLIENT_SECRET` | Secret | Enables CheckMarx scan (Job 5) |
| `FOD_CLIENT_SECRET` | Secret | Enables Fortify scan (Job 6) |
| `SCA_ENFORCEMENT_MODE` | Variable | `enforce` (default) / `warn` / `off` |
| `DELTA_FROM_COMMIT` | Variable | Fallback baseline SHA for delta calculation |
| `COVERAGE_THRESHOLD` | Variable | Apex coverage minimum % (default: 85) |
| `CRT_JOB_ID` | Variable | CRT job ID to trigger (default: 115686) |
| `CRT_PROJECT_ID` | Variable | CRT project ID (default: 73283) |
| `CRT_ORG_ID` | Variable | CRT org ID (default: 43532) |

---

## Related Docs

- [Pipeline Overview](./pipeline-overview.md)
- [Setup & Configuration](./pipeline-setup.md)
- [SCA Waivers](./sca-waivers.md)
- [Manual Runbook](./manual_runbook.md)
- [Troubleshooting](./troubleshooting.md)
