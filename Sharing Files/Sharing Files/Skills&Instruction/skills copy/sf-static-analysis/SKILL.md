---
name: sf-static-analysis
description: "Use when running Salesforce Code Analyzer static analysis on Apex, LWC, or JavaScript. Covers PMD, ESLint, RetireJS, Graph Engine, and CPD engines. Trigger phrases: run scanner, static analysis, PMD, ESLint, code analyzer, sfdx-scanner."
---

Run all applicable engines in a **single command** against the target. Replace `<target>` with the actual file or directory path.

## Preferred: single-command execution

Run one command with all engines. The scanner automatically selects applicable engines per file type:

```
sf scanner run --target "<target>" --format csv --outfile /tmp/scanner-results.csv
```

- This runs PMD, ESLint, RetireJS, and CPD in one pass.
- Graph Engine requires a separate invocation (see below).
- If the command exits with findings, the CSV file will still be written — exit code 0 means no findings; non-zero means findings exist or an error occurred.

## Engine applicability (for logging skipped engines)

| Engine       | Run when target contains            |
| ------------ | ----------------------------------- |
| PMD          | .cls or .trigger files              |
| ESLint       | .js or .html LWC files              |
| RetireJS     | .js files or package.json           |
| Graph Engine | Apex with callouts or sharing logic |
| CPD          | Any source files                    |

After the run, check the CSV output for which engines produced findings. For any engine whose file type was absent, log: "Engine `<name>` — not applicable: no `<file type>` files in scope."

## Graph Engine — separate invocation (optional)

Graph Engine requires its own run due to additional analysis time:

```
sf scanner run --target "<target>" --engine "graph" --format csv --outfile /tmp/scanner-graph-results.csv
```

If Graph Engine is not installed, note: "Engine `graph` — not run: Graph Engine not installed." This is not a blocking failure.

## Fallback: per-engine execution

Only if the single-command approach fails, fall back to per-engine runs:

```
sf scanner run --target "<target>" --engine "pmd" --format csv --outfile /tmp/scanner-pmd.csv
sf scanner run --target "<target>" --engine "eslint" --format csv --outfile /tmp/scanner-eslint.csv
sf scanner run --target "<target>" --engine "retire-js" --format csv --outfile /tmp/scanner-retirejs.csv
sf scanner run --target "<target>" --engine "cpd" --format csv --outfile /tmp/scanner-cpd.csv
```

## CSV column mapping

The scanner CSV output contains these columns (map to the review CSV):

| Scanner CSV Column | Maps to Review CSV Column |
| ------------------ | ------------------------- |
| `Problem`          | Issue                     |
| `File`             | Component (extract filename) |
| `Severity`         | Severity (1=Critical, 2=High, 3=Medium, 4+=Low) |
| `Line`             | Location (use `File:Line`) |
| `Column`           | Location (append to Line if present) |
| `Rule`             | Reference                 |
| `Description`      | Suggestion                |
| `URL`              | (discard — do not fetch)  |
| `Category`         | Category                  |
| `Engine`           | Type (prefix: `code-analyzer`) |

### Severity number mapping

| Scanner Severity | Review Severity |
| ---------------- | --------------- |
| 1                | Critical        |
| 2                | High            |
| 3                | Medium          |
| 4, 5             | Low             |

## Merge protocol

1. Read the scanner CSV output file(s).
2. Map each row using the column mapping above.
3. Set `Type = code-analyzer` for all scanner findings.
4. Merge with `Type = agent-review` findings from other steps.
5. Deduplicate by `(Component, Category, Issue, Location)` — keep the higher severity if duplicated.
6. Write the final merged CSV.

## Output requirements

For every finding report:

- Rule name
- Engine
- Severity (mapped to Critical/High/Medium/Low)
- File path + line number
- Rule category (as reported by the scanner output)

If an engine fails to run, state: "Engine `<name>` did not run — `<error>`." Add a row in the CSV with `Issue = "Engine <name> did not run: <error>"` and `Severity = High`.

Source: Salesforce Code Analyzer — PMD, ESLint, RetireJS, Graph Engine, CPD
