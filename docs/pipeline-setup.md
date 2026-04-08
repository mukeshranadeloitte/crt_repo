# UAT Pipeline — Setup & Configuration

Complete reference for all secrets and variables required by `.github/workflows/e2e-uat-pipeline.yml`.

---

## 1. GitHub Repository Secrets

Set these under **Settings → Secrets and variables → Actions → Secrets**.

### Salesforce

| Secret | Required | Description |
|--------|----------|-------------|
| `CRT_UAT_AUTHURL` | ✅ Yes | SFDX auth URL for the UAT org. Generate with: `sf org display --target-org <alias> --verbose` and copy the `Sfdx Auth Url` field. |

### CheckMarx AST

> Only needed if running CheckMarx scans. If absent, the `checkmarx-sast` job is skipped.

| Secret | Required | Description |
|--------|----------|-------------|
| `CX_BASE_URI` | ✅ | CheckMarx AST server base URL (e.g. `https://ast.checkmarx.net`) |
| `CX_TENANT` | ✅ | CheckMarx tenant name |
| `CX_CLIENT_ID` | ✅ | OAuth client ID |
| `CX_CLIENT_SECRET` | ✅ | OAuth client secret (presence of this secret enables the job) |
| `CX_PROJECT_NAME` | ⬜ Optional | Project name in CheckMarx; defaults to repository name |

### Fortify on Demand

> Only needed if running Fortify scans. If absent, the `fortify-sast-dast` job is skipped.

| Secret | Required | Description |
|--------|----------|-------------|
| `FOD_CLIENT_ID` | ✅ | FoD OAuth client ID |
| `FOD_CLIENT_SECRET` | ✅ | FoD OAuth client secret (presence of this secret enables the job) |
| `FOD_APP_NAME` | ✅ | Application name in Fortify FoD |
| `FOD_RELEASE_NAME` | ✅ | Release name in Fortify FoD |
| `FOD_DAST_SCAN_URL` | ⬜ Optional | Target URL for DAST scan. If absent, DAST steps are skipped. |

### Copado Robotic Testing (CRT)

| Secret | Required | Description |
|--------|----------|-------------|
| `CRT_PAT` | ✅ | External Personal Access Token from Copado EU Robotic instance |

---

## 2. GitHub Repository Variables

Set these under **Settings → Secrets and variables → Actions → Variables**.

### Salesforce

| Variable | Default | Description |
|----------|---------|-------------|
| `ORG_ALIAS` | `uat` | Alias used when authenticating to the target SF org |
| `DELTA_FROM_COMMIT` | *(none — required)* | Baseline commit SHA for `sfdx-git-delta`. Set to the SHA of the last successfully deployed commit. Update after each successful deployment. |
| `COVERAGE_THRESHOLD` | `85` | Minimum Apex coverage % enforced by the workflow coverage check |
| `SOURCE_DIR` | `force-app/main/default` | Source directory passed to `sf scanner run` and fallback deploy |

### Fortify on Demand

| Variable | Default | Description |
|----------|---------|-------------|
| `FOD_URL` | *(none)* | Fortify FoD instance URL (e.g. `https://ams.fortify.com`) |
| `FOD_DAST_ASSESSMENT_TYPE` | `Dynamic Assessment` | FoD DAST assessment type |
| `FOD_DAST_FREQUENCY` | `SingleScan` | FoD DAST scan frequency |
| `FOD_DAST_ENVIRONMENT` | `External` | FoD DAST environment type |

### Copado Robotic Testing (CRT)

| Variable | Default | Description |
|----------|---------|-------------|
| `CRT_JOB_ID` | `115686` | CRT Job ID to trigger (from the job URL) |
| `CRT_PROJECT_ID` | `73283` | CRT Project ID (from the job URL `?projectId=...`) |
| `CRT_ORG_ID` | `43532` | CRT Org ID (from the job URL `&orgId=...`) |

---

## 3. GitHub Environment: ReleaseGate

The `manual-validation` job (Job 7) requires a GitHub **Environment** named `ReleaseGate` to be configured.

1. Go to **Settings → Environments → New environment**
2. Name it exactly: `ReleaseGate`
3. Add required reviewers (the people who must approve before deployment)
4. Optionally set a wait timer

The environment URL points to [manual_runbook.md](./manual_runbook.md).

---

## 4. Branch Protection Rules

For the merge gate to work correctly, configure branch protection on `uat`:

1. Go to **Settings → Branches → Add rule** for branch `uat`
2. Enable **Require status checks to pass before merging**
3. Add the following as required checks:
   - `Salesforce PR validation`
   - `SCA/SAST Stage`
   - `Automated Hard Gates`
   - `CheckMarx AST Scan` *(if using CheckMarx)*
   - `Fortify on Demand Scan` *(if using Fortify)*
4. Enable **Require pull request reviews before merging** (at least 1 approval)
5. Enable **Dismiss stale pull request approvals when new commits are pushed**
6. Enable **Require branches to be up to date before merging**

---

## 5. Quick Start Checklist

```
[ ] Secret CRT_UAT_AUTHURL set to valid SFDX auth URL
[ ] Variable DELTA_FROM_COMMIT set to baseline commit SHA
[ ] Environment ReleaseGate created with required reviewers
[ ] Branch protection configured on uat branch
[ ] (Optional) CheckMarx secrets configured
[ ] (Optional) Fortify secrets and variables configured
[ ] (Optional) CRT_JOB_ID / CRT_PROJECT_ID / CRT_ORG_ID variables set
```

---

## 6. Updating DELTA_FROM_COMMIT After Each Deploy

After every successful deployment, update the variable to the new baseline:

1. Go to **Settings → Secrets and variables → Actions → Variables**
2. Edit `DELTA_FROM_COMMIT`
3. Set it to the merge commit SHA from the last successful run (visible in the `Deploy merged commit` job logs)

Or automate it by adding a step at the end of `deploy-after-merge`:

```yaml
- name: Update DELTA_FROM_COMMIT variable
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh api --method PATCH \
      "repos/${{ github.repository }}/actions/variables/DELTA_FROM_COMMIT" \
      -f value="${{ needs.approval-merge-gate.outputs.merge_commit_sha }}"
```

---

## Related Docs

- [Pipeline Overview](./pipeline-overview.md)
- [Manual Runbook](./manual_runbook.md)
- [Troubleshooting](./troubleshooting.md)
