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

## Rollback Procedure

If a deployment needs to be reverted after merging to UAT, follow these steps.

### When to Rollback

- CRT smoke tests fail after deployment
- Post-deployment defect found in UAT org
- Deployment caused an unexpected regression
- Business decision to revert a feature

### How It Works

The rollback job **inverts the forward delta**:

| What the PR did | What rollback does |
|---|---|
| **Added** new Apex classes, triggers, objects, fields | **Deletes** them (destructive change) |
| **Modified** existing components | **Re-deploys** the prior version from rollback commit |
| **Deleted** components | **Re-deploys** them from rollback commit |
| **Created new metadata** (custom objects, fields, etc.) | **Deleted** — treated as destructive |

### Step-by-Step Rollback

**1. Find the rollback-to commit SHA**

This is the last known-good commit — the state of the `uat` branch **before** the PR was merged.

```bash
# In your local repo
git log --oneline uat | head -10
# Pick the commit BEFORE the PR merge commit
```

Or find it in GitHub: `uat` branch → **Commits** → the commit just before the merge.

**2. Trigger the rollback workflow**

Go to: **Actions** → **UAT End-to-End Pipeline** → **Run workflow**

Fill in:
| Field | Value |
|-------|-------|
| **Action** | `rollback` |
| **rollback_commit_sha** | The commit SHA from step 1 (e.g. `a1b2c3d4`) |
| **rollback_pr_number** | *(Optional)* PR number that was deployed — for the comment |

Click **Run workflow**.

**3. Monitor the rollback**

The **🔄 Rollback Deployment** job will:
1. Build reverse delta (what was added → becomes destructive)
2. Display the rollback package.xml and destructiveChanges.xml before executing
3. Deploy to the UAT org with `--pre-destructive-changes` to delete new metadata first
4. Run `RunLocalTests` if Apex was involved
5. Post a PR comment and Step Summary with the result

**4. Verify**

After rollback completes:
- [ ] Check Salesforce Setup → Deployment Status in UAT
- [ ] Smoke test the reverted components
- [ ] Confirm new metadata (custom objects/fields) have been removed from the org
- [ ] Notify QA team to re-test

### Rollback Artifact

Every successful deployment uploads a `rollback-manifest-<run_id>` artifact (retained 30 days) containing:

| File | Content |
|------|---------|
| `deployed-commit.txt` | The SHA that was deployed |
| `rollback-to-commit.txt` | The SHA to revert to (HEAD^) |
| `forward-package.xml` | Components that were deployed |
| `forward-destructive.xml` | Components that were deleted by the PR |

Download this artifact from the original deploy run to confirm the correct rollback target.

### Rollback Limitations

- Rollback **cannot restore data** — if the deployment changed object structure (e.g. removed a required field), records may be affected
- Rollback of **sharing rules, permission sets, and profiles** should be reviewed manually after execution
- If multiple PRs were merged after the target PR, rolling back one may conflict with later deployments — coordinate with the team

---

## Related Docs

- [Pipeline Overview](./pipeline-overview.md)
- [Setup & Configuration](./pipeline-setup.md)
- [Troubleshooting](./troubleshooting.md)
- [SCA Waivers](./sca-waivers.md)
