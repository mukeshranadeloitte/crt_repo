# SCA & Code Quality Violation Waivers

The pipeline supports time-boxed suppression of two categories of violations:
1. **Salesforce Code Analyzer rule violations** — managed via `.github/sf-scanner-waivers.csv` (main branch only)
2. **npm dependency vulnerabilities** — managed via `.github/sca-waivers.json`

> ⚠️ **SF Code Analyzer waivers are in the `main` branch and protected.** The pipeline always fetches waivers from `main` via GitHub API — local copies in PR branches are ignored. Developers cannot approve their own waivers.

---

## SCA Enforcement Mode

The `SCA_ENFORCEMENT_MODE` repository variable controls how the Salesforce Code Analyzer scan results are handled across Jobs 2 and 4:

| Value | Behaviour |
|-------|-----------|
| `enforce` | **(Default)** Expired waivers **fail** the pipeline. Unwaived violations are warnings only. |
| `warn` | Nothing fails. All expired waivers and unwaived violations are informational warnings. |
| `off` | **All SCA steps are skipped entirely.** Use during initial project phase to bypass violations while the pipeline is being set up. |

**Set in:** Settings → Variables → Actions → `SCA_ENFORCEMENT_MODE`

> **Tip:** Set `SCA_ENFORCEMENT_MODE=off` when first onboarding a project to get the rest of the pipeline working before addressing code quality findings. Switch to `enforce` before going to production.

---

## Part 1 — Salesforce Code Analyzer Waivers

**File:** `.github/sf-scanner-waivers.csv` — **main branch only**

### How It Works

During the `Salesforce PR Validation` job:

1. `sf scanner run` produces `sfdx-report.csv` with violations at severity ≥ 3 (changed files only)
2. Pipeline fetches `.github/sf-scanner-waivers.csv` from **main branch** via GitHub API
3. Each violation is checked against fetched waivers:
   - **Active waiver** (`expiry` ≥ today, `status=ACTIVE`) → `WAIVED ✅`, job continues
   - **Expiring soon** (active, ≤30 days to expiry) → `WAIVED_EXPIRING_SOON ⏰`, warning posted
   - **Expired waiver** (`expiry` < today) → `EXPIRED_WAIVER ❌`, **job FAILS**
   - **No waiver** → `VIOLATION ⚠️`, warning + suggested waiver row printed, job continues
4. A governance report (`sca-governance-report.csv`) is uploaded as artifact
5. A PR comment table is posted (previous comment deleted before posting to avoid duplicates)

> The pipeline only fails on **expired** waivers. Unwaived violations do not block the PR.

---

### Governance

```
Developer → PR against main → Tech Lead approval → merge into main
```

| Role | Responsibility |
|------|---------------|
| **Developer** | Identifies violation, raises PR **against `main`** adding waiver row, references Jira ticket |
| **Tech Lead / Senior Engineer** | Reviews justification and expiry (max 30 days), approves PR; username goes in `approved_by` |
| **Security / DevOps Team** | Required for critical (severity 1–2); max 7-day waiver |

**Process:**
1. Check `sca-governance-report.csv` artifact — it shows the suggested CSV row for the violation
2. Raise a PR **against `main`** adding the row to `.github/sf-scanner-waivers.csv`
3. Tech Lead approves and merges — `approved_by` must match their GitHub username
4. Next PR run fetches updated CSV from main and marks violation as `WAIVED`
5. Set reminder before `expiry` to fix or renew
6. Once fixed: update `status` to `REVOKED` (keep row for audit trail — do NOT delete)

---

### Waiver File Schema

```csv
rule,file_pattern,message_contains,severity_threshold,expiry,reason,approved_by,approved_date,ticket,status
ApexDoc,MyClass.cls,,3,2026-05-10,Reason here. Tracked in PROJ-123.,jane-techlead,2026-04-10,PROJ-123,ACTIVE
```

| Column | Required | Description |
|--------|----------|-------------|
| `rule` | ✅ | Rule name substring match (e.g. `ApexDoc`) |
| `file_pattern` | ✅ | Filename substring match (e.g. `MyClass.cls`) |
| `message_contains` | ⬜ | Optional substring of violation message to narrow match |
| `severity_threshold` | ⬜ | Only waive at this severity or above (blank = any) |
| `expiry` | ✅ | DD-MM-YYYY preferred (also accepts DD/MM/YYYY and YYYY-MM-DD) — pipeline **FAILS** after this date (in `enforce` mode) |
| `reason` | ✅ | Business justification with Jira reference |
| `approved_by` | ✅ | GitHub username of approver |
| `approved_date` | ✅ | Approval date `YYYY-MM-DD` |
| `ticket` | ✅ | Jira/GitHub issue ID |
| `status` | ✅ | `ACTIVE` or `REVOKED` |

---

### Expiry Policy

| Severity | Max Duration | Required Approver |
|----------|-------------|-------------------|
| Low / Medium (3–4) | 30 days | Tech Lead |
| High (2) | 14 days | Tech Lead + Senior Eng |
| Critical (1) | 7 days | Security / DevOps |

---

### Governance Report CSV Columns

The `sca-governance-report.csv` artifact:

| Column | Description |
|--------|-------------|
| `Status` | `WAIVED`, `WAIVED_EXPIRING_SOON`, `EXPIRED_WAIVER`, `VIOLATION` |
| `Rule` | Scanner rule name |
| `File` | Source file path |
| `Line` | Line number |
| `Severity` | Violation severity |
| `Description` | Violation message |
| `Expiry` | Waiver expiry date |
| `Days_Left` | Days until expiry (negative = already expired) |
| `Reason` | Waiver reason |
| `Approved_By` | Approver GitHub username |
| `Approved_Date` | Date approved |
| `Ticket` | Tracking ticket |

---

## Part 2 — npm Dependency SCA Waivers

**File:** `.github/sca-waivers.json`

### How It Works

During the `SCA/SAST Stage` job:

1. `npm audit --json` runs and captures all high/critical vulnerabilities
2. Each violation is checked against the waiver file:
   - **Active waiver** (`expires` ≥ today) → bypassed with a ⏳ warning in the logs
   - **Expired waiver** (`expires` < today) → job **fails** with `❌ EXPIRED WAIVER`
   - **No waiver** → job **fails** with `❌ UNWAIVED`
3. A summary is printed showing waived vs failing violations
4. The full `npm audit` JSON is uploaded as the `sca-audit-report` artifact

---

### Waiver File Schema

```json
{
  "package":     "vulnerable-package-name",
  "severity":    "high",
  "advisory":    "GHSA-xxxx-xxxx-xxxx",
  "reason":      "No fix available; mitigated by WAF rule WA-123. Tracked in JIRA-456.",
  "expires":     "YYYY-MM-DD",
  "approved_by": "security-team"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `package` | string | ✅ | Exact npm package name as reported by `npm audit` |
| `severity` | `high` \| `critical` | ✅ | Severity level of the violation |
| `advisory` | string | ⬜ Optional | GHSA or CVE ID for reference |
| `reason` | string | ✅ | Business justification; include Jira ticket and mitigation |
| `expires` | `YYYY-MM-DD` | ✅ | Hard deadline — pipeline fails again after this date |
| `approved_by` | string | ✅ | Team or person who approved the waiver |

---

### How to Add a Waiver

1. **Find the package name** from the audit output:
   ```bash
   npm audit --json | jq '[.vulnerabilities | to_entries[] | .value | select(.severity == "high" or .severity == "critical") | {name, severity, via: [.via[] | .source // .]}]'
   ```

2. **Open** `.github/sca-waivers.json`

3. **Add an entry** — see example below

4. **Commit and push** as part of your PR — the waiver change will be visible in the PR diff for reviewers to approve

5. **Set a reminder** before the expiry date to either fix the vulnerability or renew the waiver

---

### Example

```json
{
  "package":     "lodash",
  "severity":    "high",
  "advisory":    "GHSA-jf85-cpcp-j695",
  "reason":      "Awaiting lodash 4.17.22 release. No consumer of affected function. Tracked in JIRA-789.",
  "expires":     "2026-09-01",
  "approved_by": "platform-security"
}
```

---

### Waiver Expiry & Renewal

When a waiver expires the pipeline will fail with:
```
❌ EXPIRED WAIVER [high] lodash (advisory: GHSA-jf85-cpcp-j695)
   Waiver expired on 2026-09-01 — fix is now required.
```

**Options:**
- **Fix the vulnerability** — update the package, then remove the waiver entry
- **Renew the waiver** — update the `expires` date and commit with a new approval comment. Requires justification for why the vulnerability still cannot be fixed.

---

### Governance Guidelines

- **Maximum waiver duration:** 90 days (recommended); no waiver should exceed 6 months without re-approval
- **Critical severity:** Require security-team sign-off before merging
- **High severity:** Require at least one senior engineer approval
- **All waivers** must reference a Jira/work item tracking the fix

---

## Related Docs

- [Pipeline Overview](./pipeline-overview.md)
- [Setup & Configuration](./pipeline-setup.md)
- [Troubleshooting](./troubleshooting.md)
