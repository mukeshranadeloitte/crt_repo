# SCA Violation Waivers

The pipeline supports time-boxed suppression of known SCA (dependency audit) violations via a waiver file. This allows teams to continue shipping while tracking outstanding security debt with a hard deadline.

---

## Waiver File Location

```
.github/sca-waivers.json
```

This file is committed to the repository and version-controlled. All waivers are visible in the PR diff and require review.

---

## How It Works

During the `SCA/SAST Stage` job:

1. `npm audit --json` runs and captures all high/critical vulnerabilities
2. Each violation is checked against the waiver file:
   - **Active waiver** (`expires` ≥ today) → bypassed with a ⏳ warning in the logs
   - **Expired waiver** (`expires` < today) → job **fails** with `❌ EXPIRED WAIVER`
   - **No waiver** → job **fails** with `❌ UNWAIVED`
3. A summary is printed showing waived vs failing violations
4. The full `npm audit` JSON is uploaded as the `sca-audit-report` artifact

---

## Waiver File Schema

```json
[
  {
    "package":     "vulnerable-package-name",
    "severity":    "high",
    "advisory":    "GHSA-xxxx-xxxx-xxxx",
    "reason":      "No fix available; mitigated by WAF rule WA-123. Tracked in JIRA-456.",
    "expires":     "YYYY-MM-DD",
    "approved_by": "security-team"
  }
]
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

## How to Add a Waiver

1. **Find the package name** from the audit output:
   ```bash
   npm audit --json | jq '[.vulnerabilities | to_entries[] | .value | select(.severity == "high" or .severity == "critical") | {name, severity, via: [.via[] | .source // .]}]'
   ```

2. **Open** `.github/sca-waivers.json`

3. **Add an entry**:
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

4. **Commit and push** as part of your PR — the waiver change will be visible in the PR diff for reviewers to approve

5. **Set a reminder** before the expiry date to either fix the vulnerability or renew the waiver

---

## Waiver Expiry & Renewal

When a waiver expires the pipeline will fail with:
```
❌ EXPIRED WAIVER [high] lodash (advisory: GHSA-jf85-cpcp-j695)
   Waiver expired on 2026-09-01 — fix is now required.
```

**Options:**
- **Fix the vulnerability** — update the package, then remove the waiver entry
- **Renew the waiver** — update the `expires` date and commit with a new approval comment. Requires justification for why the vulnerability still cannot be fixed.

---

## Example Scenarios

### Scenario 1 — Temporary suppression while waiting for upstream fix
```json
{
  "package": "semver",
  "severity": "high",
  "advisory": "GHSA-c2qf-rxjj-qqgw",
  "reason": "Upstream fix in semver@7.5.2 not yet released. Package not used in production code path. Tracked JIRA-101.",
  "expires": "2026-06-30",
  "approved_by": "devsecops-team"
}
```

### Scenario 2 — Package used only in dev/test (not production)
```json
{
  "package": "jest-circus",
  "severity": "high",
  "advisory": "GHSA-xxxx-yyyy-zzzz",
  "reason": "Vulnerability is in test runner only; not deployed to any environment. Tracked JIRA-202.",
  "expires": "2026-12-31",
  "approved_by": "security-team"
}
```

---

## Governance Guidelines

- **Maximum waiver duration:** 90 days (recommended); no waiver should exceed 6 months without re-approval
- **Critical severity:** Require security-team sign-off before merging
- **High severity:** Require at least one senior engineer approval
- **All waivers** must reference a Jira/work item tracking the fix

---

## Related Docs

- [Pipeline Overview](./pipeline-overview.md)
- [Setup & Configuration](./pipeline-setup.md)
- [Troubleshooting](./troubleshooting.md)
