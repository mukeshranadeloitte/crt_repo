# Manual Runbook — UAT Deployment Gate

This runbook guides the approver through the PR review and deployment process for the UAT Salesforce org.

---

## When Is This Runbook Used?

The automated pipeline handles all checks and gates. Human action is only required to:
1. **Review and approve the PR** in GitHub (triggers merge + deploy)
2. **Monitor and verify** the deployment after it completes

> ℹ️ The `ReleaseGate` manual approval step has been removed. The PR review approval (`ss10del` / `chorevathi-deloitte`) is the single human gate before deployment.

## Automated Jobs Summary

| # | Job | Depends On | Description |
|---|-----|------------|-------------|
| 1 | `setup` | — | Evaluates which security scanners to run; outputs `run-checkmarx` / `run-fortify` flags |
| 2 | `salesforce-validation` | *(none — starts immediately)* | Requests reviewers (`ss10del`, `chorevathi-deloitte`), validates delta, runs SF Code Analyzer |
| 3 | `checkmarx-sast` | `setup` | CheckMarx SAST (runs in **parallel** with Job 4, conditional on `CX_CLIENT_SECRET`) |
| 4 | `fortify-sast-dast` | `setup` | Fortify SAST/DAST (runs in **parallel** with Job 3, conditional on `FOD_CLIENT_SECRET`) |

> Jobs 2, 3, and 4 all run in **parallel** on PR open/update. Once all pass, the PR is ready for human review/approval.

---

## Pre-Approval Checklist

### 1. Review the Pull Request

- [ ] PR description clearly explains what is being changed and why
- [ ] Linked to a Jira/work item or change ticket
- [ ] No unresolved review comments

### 2. Validate Artifacts

Go to the **Actions** run for this PR and download/review:

| Artifact | What to Check |
|----------|--------------|
| `salesforce-delta-validation` | `package.xml` lists expected components; `destructiveChanges.xml` is intentional |
| `salesforce-code-analyzer-csv` | No unexpected high-severity findings |
| `sfdx-report` | No critical issues introduced by this change |
| `checkmarx-sarif-report` | No new high/critical SAST findings *(if CheckMarx enabled)* |
| `fortify-sast-sarif-report` | No new critical SAST findings *(if Fortify enabled)* |

### 3. Check Test Coverage

- [ ] Apex test coverage is ≥ 85% per class (configurable via `COVERAGE_THRESHOLD`; enforced by platform — deployment will fail if not met)
- [ ] The right test classes are being run (verify in the `Validate deploy` step logs)

### 4. Destructive Changes

If `destructiveChanges.xml` is present:

- [ ] Confirm a data backup has been completed for any affected objects
- [ ] Confirm downstream systems/integrations are not impacted
- [ ] Change has been reviewed and approved by the org admin

### 5. Deployment Window

- [ ] Deployment is within the approved change window
- [ ] UAT org is not locked or in maintenance
- [ ] Downstream QA team has been notified

---

## How to Approve a PR for Deployment

Once all automated checks are green:

1. Open the PR on GitHub
2. Review the **Artifacts** from the Actions run (delta package, scanner reports)
3. Click **Approve** on the PR (as `ss10del` or `chorevathi-deloitte`)

The `approval-merge-gate` job triggers automatically on your approval and will:
- Verify the approval is for the latest commit SHA (stale approvals are rejected)
- Confirm all required checks passed
- Auto-merge the PR
- Deploy to UAT org
- Trigger CRT smoke tests

---

## How to Reject a PR

Request changes on the PR in GitHub. The developer must address the feedback, push a new commit, and the pipeline will re-run automatically.

Leave a review comment explaining the rejection reason so the developer can act on it.

---

## Post-Deployment Verification

After the deploy completes (Job 8), verify in UAT:

- [ ] Smoke test the deployed components manually or via CRT
- [ ] Check Salesforce Setup → Deployment Status for any warnings
- [ ] Confirm no production-impacting data changes
- [ ] CRT job triggered (check [CRT Dashboard](https://eu-robotic.copado.com/jobs/115686?projectId=73283&orgId=43532))

---

## Escalation Contacts

| Issue | Contact |
|-------|---------|
| Pipeline failures | DevOps / Platform Engineering team |
| Salesforce org issues | Salesforce Admin / Architect |
| CRT test failures | QA / Test Automation team |
| Security scan findings | Security team |

---

## Rollback / Reverting a Deployment

The pipeline no longer has an automated rollback job. If a deployment needs reverting after merging to UAT, it must be done **manually in the Salesforce org**:

1. Go to **Salesforce Setup → Deployment Status** in the UAT org
2. Identify the deployment to revert
3. Manually redeploy the previous known-good version using the Salesforce CLI or Workbench
4. Notify QA team to re-test after the manual revert

---

## Related Docs

- [Pipeline Overview](./pipeline-overview.md)
- [Setup & Configuration](./pipeline-setup.md)
- [Troubleshooting](./troubleshooting.md)
- [SCA Waivers](./sca-waivers.md)
