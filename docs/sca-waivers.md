# SCA & Code Quality Violation Waivers

The pipeline supports time-boxed suppression of two categories of violations:
1. **npm dependency vulnerabilities** — managed via `.github/sca-waivers.json`
2. **Salesforce Code Analyzer rule violations** — managed via `.github/sf-scanner-waivers.json`

Both files are committed to the repository and version-controlled. All waiver changes are visible in the PR diff and require peer review.

---

## Part 1 — Salesforce Code Analyzer Waivers

**File:** `.github/sf-scanner-waivers.json`

### How It Works

During the `Salesforce PR Validation` job:

1. `sf scanner run` produces `sfdx-report.csv` with all violations at severity ≥ 3
2. Each violation is checked against the waiver file:
   - **Active waiver** (`expiry` ≥ today) → logged as `WAIVED ✅`, job **continues**
   - **Expired waiver** (`expiry` < today) → logged as `EXPIRED_WAIVER ⚠️`, written to results CSV, job **continues** (`continue-on-error: true`)
   - **No waiver** → logged as `VIOLATION ⚠️`, written to results CSV, job **continues**
3. Both `sfdx-report.csv` (raw scanner output) and `sfdx-waiver-results.csv` (annotated results) are uploaded as the `sfdx-scanner-reports` artifact

> **Note:** The PR Validation job never fails due to scanner violations. The CSV artifacts provide full visibility for reviewers.

---

### Who Can Update the Waiver File & Process

```
Developer  →  Tech Lead  →  [Security Team if Critical]  →  Merge
```

| Role | Responsibility |
|------|---------------|
| **Developer** | Identifies violation, creates waiver entry in feature branch PR, references Jira ticket |
| **Tech Lead / Senior Engineer** | Reviews justification and expiry date, approves PR, their username goes in `approved_by` |
| **Security / DevOps Team** | Required approver for critical severity violations; max 7-day waiver |

**Step-by-step process:**
1. Developer encounters a violation they cannot fix immediately (e.g., tech debt, refactoring in progress)
2. Developer adds an entry to `.github/sf-scanner-waivers.json` in their feature branch
3. Developer opens a PR — the waiver diff is explicitly visible to reviewers
4. Tech Lead reviews the justification, expiry date (max 30 days), and Jira ticket reference
5. Tech Lead approves; the `approved_by` field must match their GitHub username
6. Developer sets a calendar reminder before `expiry` to fix the violation or renew the waiver
7. Once the violation is fixed, the entry **must** be removed in the same PR as the fix

---

### Waiver File Schema

```json
{
  "rule":        "ApexDoc",
  "file":        "MyClass.cls",
  "description": "Missing ApexDoc comment on all public methods",
  "expiry":      "2026-05-01",
  "reason":      "Refactoring in sprint 12. Tracked in PROJ-123.",
  "approved_by": "tech-lead-github-username",
  "ticket":      "PROJ-123"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `rule` | ✅ | Rule name from the scanner report — partial substring match (e.g. `"ApexDoc"`) |
| `file` | ✅ | Filename from the scanner report — partial match (e.g. `"MyClass.cls"`) |
| `description` | ✅ | Human-readable description of the violation |
| `expiry` | ✅ | Hard deadline `YYYY-MM-DD` — pipeline writes to violation CSV after this date |
| `reason` | ✅ | Business justification — must include Jira/work-item reference |
| `approved_by` | ✅ | GitHub username of the approving Tech Lead |
| `ticket` | ⬜ Recommended | Jira or work-item ID tracking the fix |

---

### Expiry Policy

| Severity | Max Duration | Approver Required |
|----------|-------------|-------------------|
| Low / Medium | 30 days | Tech Lead |
| High | 14 days | Tech Lead + Senior Eng |
| Critical | 7 days | Security Team |

---

### Example — Add a Waiver

Find the rule name from the scanner report artifact (`sfdx-report.csv`). Then add to `.github/sf-scanner-waivers.json`:

```json
{
  "rule": "ApexDoc",
  "file": "CoverageDemoService.cls",
  "description": "Missing ApexDoc comments on public methods in CoverageDemoService",
  "expiry": "2026-05-01",
  "reason": "ApexDoc to be added during sprint 12 refactoring. Tracked in PROJ-123.",
  "approved_by": "jane-techlead",
  "ticket": "PROJ-123"
}
```

---

### Results CSV Format

The `sfdx-waiver-results.csv` artifact (in `sfdx-scanner-reports`) has columns:

| Column | Description |
|--------|-------------|
| `Status` | `WAIVED`, `EXPIRED_WAIVER`, or `VIOLATION` |
| `Rule` | Scanner rule name |
| `File` | Source file path |
| `Line` | Line number |
| `Severity` | Violation severity |
| `Description` | Violation description |
| `Expiry` | Waiver expiry date (if waived) |
| `Reason` | Waiver reason (if waived) |
| `Approved_By` | Approver username (if waived) |
| `Ticket` | Tracking ticket (if waived) |

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
