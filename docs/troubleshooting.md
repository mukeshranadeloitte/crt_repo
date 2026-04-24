# Pipeline Troubleshooting Guide

Common errors encountered in the UAT End-to-End pipeline and how to resolve them.

---

## Salesforce Validation Errors

### `No authorization information found for uat`

**Cause:** The org was not authenticated with the correct alias, or authentication failed silently.

**Fix:**
1. Verify secret `CRT_UAT_AUTHURL` is set and contains a valid SFDX auth URL
2. Regenerate the auth URL: `sf org display --target-org <alias> --verbose --json`
3. The auth URL expires if the connected app session expires — refresh it

---

### `Required repository variable 'DELTA_FROM_COMMIT' is missing or empty`

**Cause:** The `DELTA_FROM_COMMIT` Actions variable is not set.

**Fix:**
1. Go to **Settings → Secrets and variables → Actions → Variables**
2. Create (or update) a variable named `DELTA_FROM_COMMIT`
3. Set the value to a valid commit SHA that exists in the repo history — typically the last successfully deployed commit

---

### `Deploy validation failed — CoverageDemoService - Test coverage 35%, at least 75% required`

**Cause:** The Salesforce platform enforces a minimum test coverage per deployed Apex class. The workflow also enforces `COVERAGE_THRESHOLD` (default: **85%**) — both platform minimum and your threshold must be met.

**Fix — Option A (preferred):** Add or improve tests for `CoverageDemoService` until coverage reaches ≥ `COVERAGE_THRESHOLD` (default 85%).

**Fix — Option B (temporary):** Change test level to `AllLocalTests` in the validate step. This runs all tests in the org, which typically satisfies aggregate coverage. Update the workflow's deploy step:
```yaml
deploy_cmd+=(--test-level AllLocalTests)
```
> Note: This increases run time significantly.

---

### `Apex changed but no tests were specified or inferred`

**Cause:** Apex classes were modified but no test classes were found by convention or in the PR description.

**Fix:**
- Add a line to your PR description: `tests: MyClassTest, AnotherTest`
- Or ensure your test classes follow naming convention: `ClassNameTest`, `ClassNameTests`, or `ClassNameTestClass`

---

### `Required repository variable 'CRT_UAT_COMMIT_ID' is missing or empty`

**Cause:** Old double-indirection variable name referenced. This was fixed in the current pipeline version.

**Fix:** Rename the variable from `CRT_UAT_COMMIT_ID` to `DELTA_FROM_COMMIT` in repository Actions variables.

---

## Security Scan Errors

### CheckMarx job skipped unexpectedly

**Cause:** Either `CX_CLIENT_SECRET` secret is not set, or the `scanner` input was not `checkmarx` or `all`.

**Fix:**
1. Confirm `CX_CLIENT_SECRET` is set in repository secrets
2. When manually triggering, select `all` or `checkmarx` for the `scanner` input

---

### Fortify job skipped unexpectedly

**Cause:** `FOD_CLIENT_SECRET` secret is not set.

**Fix:** Add the `FOD_CLIENT_SECRET` secret under repository secrets.

---

## Approval & Merge Errors

### `Stale approval. Review commit does not match latest PR head SHA`

**Cause:** A new commit was pushed to the PR branch after the reviewer approved, making the approval stale.

**Fix:** The reviewer must re-approve after the latest commit. This is intentional stale-approval protection.

---

### `Required check 'X' has no successful run on commit <SHA>`

**Cause:** One or more required checks did not complete successfully for the current PR head SHA.

**Fix:**
1. Check which job failed in the PR checks list
2. Re-run the failed job from Actions → Re-run failed jobs
3. If all checks show green but this error still appears, the check-run names in the workflow may differ — verify the job `name:` field matches exactly what appears in the PR checks list

---

### `PR merge failed`

**Cause:** The GitHub API merge call failed. Possible reasons:
- PR is already merged
- Merge conflict exists
- Branch protection rules blocked the merge
- `GITHUB_TOKEN` lacks `contents: write` permission

**Fix:**
1. Check for merge conflicts and resolve them
2. Confirm branch protection rules are satisfied
3. Verify the workflow has `contents: write` permission (it does by default in `approval-merge-gate`)

---

## CRT (Copado Robotic Testing) Errors

### `CRT API call failed with HTTP 401`

**Cause:** Invalid or expired `CRT_API_TOKEN` token, or wrong auth header format. The CRT API uses `X-Authorization: <token>` (not `Bearer`).

**Fix:** Regenerate the External Personal Access Token in Copado EU Robotic and update the `CRT_API_TOKEN` secret.

### `CRT API call failed with HTTP 500 — Could not fetch tokens for access key`

**Cause:** The server recognises the auth header format but cannot find the key — typically means the token is for a different organisation or has been revoked.

**Fix:**
1. Confirm you are using the **EU** instance token (eu-robotic.copado.com)
2. Regenerate the token from the correct Copado org
3. Update the `CRT_API_TOKEN` secret

### `2xx but response is not JSON`

**Cause:** CRT API returns a non-JSON success response body. This is expected behaviour from this endpoint.

**Resolution:** This is not an error — the workflow handles it gracefully and logs `Run started`.

---

## General Workflow Issues

### Jobs skipping unexpectedly on `pull_request_review`

**Cause:** Jobs with `if: github.event_name == 'pull_request'` correctly skip when the event is `pull_request_review`. This is by design — the PR validation jobs only run on the PR event.

**Behaviour:** These skipped jobs create new `conclusion=skipped` check-run entries. The `approval-merge-gate` job is designed to handle this — it queries for ANY historical `success` entry, not just the most recent one.

---

### `npm audit` failing in SCA stage

**Cause:** A dependency has a high-severity vulnerability.

**Fix:**
1. Run `npm audit` locally and review the findings
2. Update the vulnerable package: `npm update <package>`
3. If the vulnerability is a false positive or has no fix, add an `.npmrc` audit exception or use `npm audit --omit=dev` if the vulnerability is only in dev dependencies

---

### `npm error ENOENT` — no such file or directory (package.json)

**Cause:** The project has no `package.json`. This happens when using the pipeline in a Salesforce project that was not originally set up as a Node.js project.

**Resolution:** The pipeline **automatically creates** a standard Salesforce `package.json` (with eslint, prettier, sfdx-lwc-jest, husky, lint-staged) if one doesn't exist before running `npm install`. No action required — this is built in to Jobs 2, 3, 8, and 10.

---

### `SyntaxError: invalid syntax` in `check-npm-waivers.py` (line: `if [ -f ... ]`)

**Cause:** When regenerating the workflow from `create-e2e-uat-pipeline.prompt.md` in a new project, an AI agent incorrectly generated a Python script via `cat > check-npm-waivers.py << 'PYTHON_SCRIPT'` and placed a bash `if [ -f ... ]` guard **inside** the Python heredoc. Python then fails to parse bash syntax.

**Root cause:** The AI agent invented a Python-based waiver checker instead of using the correct pure-bash implementation.

**Immediate fix — replace the broken step in your workflow:**

Find the step named `Run dependency SCA gate with waiver support` (or the step that creates `check-npm-waivers.py`) and replace it entirely with this:

```yaml
      - name: Run dependency SCA gate with waiver support
        run: |
          set -euo pipefail
          WAIVER_FILE=".github/sca-waivers.json"
          TODAY=$(date -u +%Y-%m-%d)
          npm audit --json --audit-level=high > audit-output.json 2>/dev/null || true
          VULN_COUNT=$(jq '[.vulnerabilities // {} | to_entries[] | .value
            | select(.severity == "high" or .severity == "critical")] | length' audit-output.json 2>/dev/null || echo 0)
          if [[ "$VULN_COUNT" -eq 0 ]]; then
            echo "✅ No high/critical vulnerabilities found."
            exit 0
          fi
          echo "Found $VULN_COUNT high/critical vulnerability/ies. Checking waivers..."
          WAIVERS="[]"
          if [[ -f "$WAIVER_FILE" ]]; then
            WAIVERS=$(jq '.' "$WAIVER_FILE" 2>/dev/null || echo "[]")
            echo "Loaded waiver file: $WAIVER_FILE"
          else
            echo "No waiver file found at $WAIVER_FILE — all violations will be evaluated."
          fi
          FAIL=0; WAIVED=0; EXPIRED=0
          while IFS= read -r vuln_json; do
            PKG=$(echo "$vuln_json"  | jq -r '.name')
            SEV=$(echo "$vuln_json"  | jq -r '.severity')
            GHSA=$(echo "$vuln_json" | jq -r '.via[0].source // .via[0] // "unknown"' 2>/dev/null | head -1)
            WAIVER=$(echo "$WAIVERS" | jq --arg pkg "$PKG" --arg today "$TODAY" \
              '[.[] | select(.package == $pkg and .expires >= $today)] | first // empty')
            EXPIRED_WAIVER=$(echo "$WAIVERS" | jq --arg pkg "$PKG" --arg today "$TODAY" \
              '[.[] | select(.package == $pkg and .expires < $today)] | first // empty')
            if [[ -n "$WAIVER" && "$WAIVER" != "null" ]]; then
              EXPIRES=$(echo "$WAIVER" | jq -r '.expires')
              REASON=$(echo "$WAIVER"  | jq -r '.reason')
              APPROVED=$(echo "$WAIVER"| jq -r '.approved_by // "unknown"')
              echo "⏳ WAIVED [$SEV] $PKG (advisory: $GHSA)"
              echo "   Reason: $REASON | Approved by: $APPROVED | Expires: $EXPIRES"
              WAIVED=$((WAIVED + 1))
            elif [[ -n "$EXPIRED_WAIVER" && "$EXPIRED_WAIVER" != "null" ]]; then
              EXPIRES=$(echo "$EXPIRED_WAIVER" | jq -r '.expires')
              REASON=$(echo "$EXPIRED_WAIVER"  | jq -r '.reason')
              echo "::error::❌ EXPIRED WAIVER [$SEV] $PKG (advisory: $GHSA)"
              echo "   Waiver expired on $EXPIRES — fix is now required. Reason was: $REASON"
              EXPIRED=$((EXPIRED + 1))
              FAIL=1
            else
              echo "::error::❌ UNWAIVED [$SEV] $PKG (advisory: $GHSA) — no active waiver found."
              FAIL=$((FAIL + 1))
            fi
          done < <(jq -c '[.vulnerabilities // {} | to_entries[] | .value
            | select(.severity == "high" or .severity == "critical")][]' audit-output.json 2>/dev/null)
          echo ""
          echo "──────────────────────────────────────────"
          echo "SCA Summary: $VULN_COUNT violation(s) found"
          echo "  ✅ Waived (active):   $WAIVED"
          echo "  ❌ Expired waivers:   $EXPIRED"
          echo "  ❌ Unwaived failures: $((FAIL - EXPIRED))"
          echo "──────────────────────────────────────────"
          if [[ "$FAIL" -gt 0 ]]; then
            echo "To suppress a known violation, add an entry to $WAIVER_FILE:"
            echo '  { "package": "<pkg>", "severity": "<high|critical>", "reason": "<justification>", "expires": "YYYY-MM-DD", "approved_by": "<team>" }'
            exit 1
          fi
          echo "✅ All violations are covered by active waivers."
```

**Prevention:** The updated `create-e2e-uat-pipeline.prompt.md` (rules 9, 10, 12, 13) and `e2e-uat-pipeline.agent.md` (Constraints section) now include the full verbatim bash implementation. When regenerating in a new project, the agent must copy this step exactly.

**Rule:** Never put bash `if [ ... ]; then` inside a `<< 'HEREDOC'` block — it will be interpreted as code in the target language, not bash.

---

### `npm error code ETARGET` — No matching version found for `@salesforce/eslint-plugin-aura@^2.4.0`

**Cause:** When regenerating the workflow from `create-e2e-uat-pipeline.prompt.md` in a new project, an AI agent used an outdated/non-existent package version for `@salesforce/eslint-plugin-aura`. Version `^2.4.0` does not exist on npm.

**Resolution:** The updated prompt now includes the **Canonical `package.json` devDependencies** section with pinned versions. Regenerate the workflow using the updated prompt. The correct version is:
```
"@salesforce/eslint-plugin-aura": "^3.0.0"
```
If you already have a generated workflow, locate the `bootstrap package.json` step and replace `^2.4.0` with `^3.0.0`.

---

## Log Locations

| Information | Where to Find |
|-------------|--------------|
| Deployment component failures | `Deploy merged changes` step → `--- component failures ---` section |
| Test failures | `Deploy merged changes` step → `--- test failures ---` section |
| Coverage warnings | `Deploy merged changes` step → `--- coverage warnings ---` section |
| Delta package contents | `Display generated packages` step |
| Code Analyzer findings | `salesforce-code-analyzer-csv` artifact or `sfdx-report` artifact |
| CheckMarx results | `checkmarx-sarif-report` artifact + GitHub Code Scanning tab |
| Fortify SAST results | `fortify-sast-sarif-report` artifact + GitHub Code Scanning tab |
| CRT run status | [CRT Dashboard](https://eu-robotic.copado.com/jobs/115686?projectId=73283&orgId=43532) |

---

## Related Docs

- [Pipeline Overview](./pipeline-overview.md)
- [Setup & Configuration](./pipeline-setup.md)
- [Manual Runbook](./manual_runbook.md)
- [SCA Waivers](./sca-waivers.md)
