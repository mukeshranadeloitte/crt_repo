Create a production-ready GitHub Actions workflow at pr-validation-uat.yml that combines:

1. Salesforce PR validation and approval-based deployment
2. SAST/DAST security scanning (CheckMarx + Fortify)

---

**Primary flow and ordering requirements:**
1. On `pull_request` to target branches, run Salesforce validation first.
2. Then run SCA/SAST stage.
3. Then run CheckMarx and Fortify scans after the SCA stage.
4. PR must not be approved for merge/deploy until all required checks pass (configure these jobs as required status checks in branch protection).
5. On `pull_request_review` submitted with APPROVED:
   - Re-verify approval is for latest PR head SHA (stale approval protection).
   - Verify required checks passed by querying all check-run entries for the SHA — accept the check as passing if **any** completed+success entry exists for that check name (not just the most recent). This is required because when `pull_request_review` fires, jobs skipped by their `if:` conditions produce new `conclusion=skipped` check-run entries that would otherwise shadow an earlier successful run on the same SHA.
   - Auto-merge the PR (Create a merge commit).
   - After merge succeeds, deploy merged code to org.
6. Deployment must run from merged commit, not from pre-merge PR head.

---

**Workflow name:**
`PR Validation UAT + Security Gates + Auto Merge + Deploy`

---

**Triggers:**
- `pull_request`
  - branches: target branch (default `uat`) and `UberDemo` support
  - types: `opened`, `reopened`, `synchronize`, `edited`, `ready_for_review`
  - paths: `force-app/**`
- `pull_request_review`
  - types: `submitted`
- `workflow_dispatch`
  - input `scanner`: `all | checkmarx | fortify`

---

**Global requirements:**
- concurrency per PR with `cancel-in-progress: true`
- least-privilege permissions per job
- strict bash mode in all script steps: `set -euo pipefail`
- values configurable via env/vars
- concise comments only for non-obvious logic
- directly runnable YAML

---

**Salesforce validation requirements:**
- checkout full history
- setup node 20
- `npm ci` if lockfile exists, else `npm install`
- install Salesforce CLI
- authenticate via SFDX auth URL secret
- install sfdx-git-delta
- build delta from baseline commit variable to HEAD
- generate and log:
  - `package/package.xml`
  - `destructiveChanges/destructiveChanges.xml`
- upload both manifests as artifacts when present
- parse tests from PR body/comments: `tests: Class1Test,Class2Test`
- infer tests by convention: `ClassNameTest`, `ClassNameTests`, `ClassNameTestClass`
- fail if Apex changed and no tests specified/inferred
- run check-only validate deploy
- if Apex changed: `RunSpecifiedTests` and pass each class via `--tests`
- if no Apex changed: `NoTestRun`
- enforce coverage threshold
- run Salesforce Code Analyzer
- generate CSV report (`scanner-report.csv`), preview in logs, upload artifact

---

**Security stage requirements:**
- add a dedicated SCA stage/job after Salesforce validation
- run CheckMarx and Fortify only after SCA stage succeeds
- `setup` job outputs:
  - `run-checkmarx`
  - `run-fortify`
- logic:
  - `run-checkmarx` true only when `CX_CLIENT_SECRET` exists and scanner is `checkmarx`/`all`
  - `run-fortify` true only when `FOD_CLIENT_SECRET` exists and scanner is `fortify`/`all`

---

**CheckMarx job:**
- needs `setup` + SCA stage
- run only if `run-checkmarx` true
- use `checkmarx/ast-github-action` with current valid immutable tag
- parameters:
  - `base_uri`: `CX_BASE_URI`
  - `cx_tenant`: `CX_TENANT`
  - `cx_client_id`: `CX_CLIENT_ID`
  - `cx_client_secret`: `CX_CLIENT_SECRET`
  - `project_name`: `CX_PROJECT_NAME` or repo name
  - `additional_params`: `--scan-types sast,kics --report-format sarif --output-path . --output-name cx_result`
- upload `cx_result.sarif` artifact
- upload SARIF to GitHub code scanning (category `checkmarx`)

---

**Fortify job:**
- needs `setup` + SCA stage
- run only if `run-fortify` true
- expose `HAS_DAST_URL` from `FOD_DAST_SCAN_URL` presence
- use supported current Fortify action for SAST
- if direct DAST input unsupported, use documented Fortify setup + `fcli` custom flow for DAST
- optional DAST runs only when `HAS_DAST_URL` true
- export/upload SAST SARIF and publish to code scanning category `fortify-sast`
- if DAST runs, upload DAST artifact/report and publish SARIF category `fortify-dast`

---

**Approval, merge, deploy requirements:**
- approval job triggers only on review state `APPROVED`
- verify `review.commit_id == pull_request.head.sha` (stale approval protection)
- verify required checks for the head SHA by calling `GET /repos/{repo}/commits/{sha}/check-runs` and checking that **at least one check-run entry** with the required name has `status=completed` AND `conclusion=success` — do NOT rely on `head -1` or the most recent entry alone, because when `pull_request_review` triggers the workflow, jobs skipped by their `if:` conditions emit new `conclusion=skipped` check-run records on the same SHA that would otherwise falsely block the gate
- merge PR automatically using GitHub API (`PUT /repos/{repo}/pulls/{number}/merge`, `merge_method=merge`)
- capture `merge_commit_sha`
- deploy job must:
  - checkout `merge_commit_sha`
  - rebuild delta/manifests
  - re-evaluate tests
  - run real deploy (not validate)
  - include destructive changes
  - `RunSpecifiedTests` when Apex changed and tests available
  - `NoTestRun` only when no Apex changes
  - print component/test/coverage diagnostics on failure

---

**Required config keys to document:**

Salesforce:
- `ORG_ALIAS`
- `SFDX_AUTH_SECRET_NAME`
- `DELTA_FROM_COMMIT_VAR`
- `COVERAGE_THRESHOLD`
- `SOURCE_DIR`

CheckMarx:
- `CX_BASE_URI`
- `CX_TENANT`
- `CX_CLIENT_ID`
- `CX_CLIENT_SECRET`
- optional `CX_PROJECT_NAME`

Fortify:
- `FOD_URL`
- `FOD_CLIENT_ID`
- `FOD_CLIENT_SECRET`
- `FOD_APP_NAME`
- `FOD_RELEASE_NAME`
- optional `FOD_DAST_SCAN_URL`

---

**Deliverables:**
1. Full YAML for pr-validation-uat.yml
2. Setup checklist with required secrets/variables and example values
3. Brief stale-approval protection explanation
4. Explicit explanation of `RunSpecifiedTests` selection and passing
5. Explicit explanation of delta/destructive manifests and analyzer CSV generation/upload
6. Explicit explanation of auto-merge flow and deployment from merge commit, including the required-checks verification logic that handles skipped check-run entries
