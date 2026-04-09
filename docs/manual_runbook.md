# Manual Runbook — UAT Deployment Gate

This runbook guides the approver through the manual validation step (`ReleaseGate`) before a PR is auto-merged and deployed to the UAT Salesforce org.

---

## When Is This Runbook Used?

This step activates **after** all automated checks pass:

- ✅ Salesforce PR validation (check-only deploy)
- ✅ Apex test coverage ≥ 75%
- ✅ Salesforce Code Analyzer — no severity-3+ findings blocking deploy
- ✅ SCA dependency audit — no high-severity vulnerabilities
- ✅ CheckMarx / Fortify scans (if configured)

A GitHub environment approval request is sent to designated reviewers. This document describes what to verify before approving.

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

- [ ] Apex test coverage is ≥ 75% per class (enforced by platform — deployment will fail if not met)
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

## How to Approve

1. Open the GitHub Actions run for this PR
2. Navigate to the **Manual Agent Validation (ReleaseGate)** job
3. Click **Review deployments**
4. Select the `ReleaseGate` environment
5. Add a comment (optional but recommended)
6. Click **Approve and deploy**

After approval, the pipeline will wait for a PR review with state `APPROVED` to trigger the merge and deploy jobs.

---

## How to Reject

Click **Reject** on the ReleaseGate approval. This cancels the workflow run. The developer must push a new commit or re-open the PR review cycle.

Leave a comment explaining the rejection reason so the developer can act on it.

---

## Post-Deployment Verification

After the deploy completes (Job 9), verify in UAT:

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

## Related Docs

- [Pipeline Overview](./pipeline-overview.md)
- [Setup & Configuration](./pipeline-setup.md)
- [Troubleshooting](./troubleshooting.md)
