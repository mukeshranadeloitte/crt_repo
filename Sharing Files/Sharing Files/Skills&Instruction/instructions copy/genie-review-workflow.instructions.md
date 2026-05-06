---
description: "GenieReview 11-step Salesforce code and architecture review workflow. Referenced by GenieReview.agent.md."
---

> Execute steps in order. Track each step with the todo tool. After Step 1, evaluate the component inventory and skip any step whose skill is not applicable to the detected component types. Log every skipped step as: Step N — skipped: no [component type] detected. Load each referenced skill file before executing that step.
>
> **Do not fetch any external URL at any point during the review.** All knowledge needed is embedded inline in the skill files. When citing a source, use the plain text `Source:` label present in each skill file.

### Output discipline

- During execution, emit only terse progress lines: `Step N complete` or `Step N — skipped: <reason>`.
- Do not emit findings tables or detailed narratives in chat during intermediate steps.
- Full detail belongs in the CSV artifact.

### Speed rules

- **Batch skill loading**: When multiple consecutive steps are all marked RUN, read their skill files together before executing them sequentially.
- **Early-exit on small inputs**: If the input contains ≤ 3 files and no triggers, flows, or batch classes, auto-skip Steps 4, 6, 9a, 9b, 9c. Log: `Step N — skipped: small input, not applicable`.
- **Single scanner command**: Run `sf scanner run` once with all engines (see Step 2). Do not run per-engine commands unless the single command fails.

---

## STEP 0 — Tool installation gate

Verify all required tools are installed before any review. Run these checks first:

```
node --version
sf --version
sf plugins --core
```

### Required tools checklist

| Tool                    | Check command       | Required for                                               |
| ----------------------- | ------------------- | ---------------------------------------------------------- |
| Node.js v18+            | `node --version`    | Salesforce CLI prerequisite                                |
| Salesforce CLI (`sf`)   | `sf --version`      | All scanning                                               |
| SF Code Analyzer plugin | `sf scanner --help` | Static analysis (PMD, ESLint, RetireJS, Graph Engine, CPD) |

### Installation protocol — HUMAN APPROVAL REQUIRED

If any tool is missing, you **MUST** use the `vscode_askQuestions` tool to ask the developer for explicit approval **before installing anything**. Present a clear list of what is missing and what will be installed.

Approval question format:

- Header: "Tool Installation Approval Required"
- List every missing tool with the exact install command
- Ask: "May I proceed to install the missing tools listed above?"
- Options: Yes – proceed with installation / No – I will install manually

**Do not run any install command until the developer answers Yes.**

If approved — install in this order:

1. If Node.js is missing:
   - Direct the developer to https://nodejs.org (cannot auto-install OS runtimes)
   - Pause and ask them to confirm once Node.js is installed
2. If Salesforce CLI is missing:
   - `npm install --global @salesforce/cli`
   - Verify: `sf --version`
3. If Code Analyzer plugin is missing:
   - `sf plugins install @salesforce/sfdx-scanner`
   - Verify: `sf scanner --help`

If the developer answers No — state the manual install commands clearly and halt. Do not proceed with review until tools are confirmed installed.

**Do not proceed past this step if tools are not confirmed installed.**

---

## STEP 1 — Input detection and component inventory

Accept these input types (detect automatically): single file, list of files, `package.xml`, design document, GitHub link.

Produce a component inventory before any analysis. Based only on what is in the input — no assumptions.

| Component | Type | Apparent purpose |
| --------- | ---- | ---------------- |

If only a design document is provided with no source code, state that static analysis cannot run and scope to architecture and data model only.

**Design document only (no source files):**
Skip Steps 2, 3, 6, 7, 8, 9a, 9b, 9c, 10 entirely.
Run only: Step 4 (architecture + over-engineering), Step 5 (data model), Step 11 (report).
State in the report header: "Source code not provided — static analysis skipped. Architecture and data model review only."

### Step 1b — Skill applicability gate

Based on the component inventory, mark each skill as RUN or SKIP:

| Skill                    | Run if input contains                                                    |
| ------------------------ | ------------------------------------------------------------------------ |
| sf-static-analysis       | Any .cls, .trigger, .js, or .html files                                  |
| sf-security              | Any Apex, LWC, Flow, or permission metadata                              |
| sf-architecture          | Any Apex trigger, Flow, handler, batch, or queueable                     |
| sf-data-model            | Custom objects, fields, relationships, or data design docs               |
| sf-governor-performance  | Any Apex trigger, batch, queueable, Flow, or SOQL-heavy class            |
| sf-test-quality          | Any @isTest class or test method                                         |
| sf-api-versioning        | Any metadata XML with apiVersion, Aura, LWC, or Flow                     |
| sf-build-forms           | Screen Flow, Dynamic Forms, Omnistudio, or form LWC                      |
| sf-event-driven          | Platform Events, CDC, Pub/Sub, or streaming patterns                     |
| sf-deployment            | package.xml, destructiveChanges.xml, CI/CD config                        |
| sf-code-quality          | Any .cls, .trigger, .js, .html, interface, abstract class, handler, service, or selector |
| sf-web-app-security      | Visualforce pages, Apex with `PageReference`/redirect, file upload Apex, static resource metadata, LWC with CSP or `innerHTML` concerns |
| sf-auth-session-security | Connected app metadata, Profile or Permission Set XML, design documents mentioning authentication, MFA, session settings, or password policy |
| sf-shield-encryption     | Permission set metadata with encryption permissions, Apex referencing encrypted fields, or design documents mentioning Shield, PII fields, or HIPAA |
| sf-audit-monitoring      | Apex querying `EventLogFile`, Transaction Security Policy metadata, design documents mentioning HIPAA/MARS-E, event monitoring, or audit trail |
| sf-resilience            | Design documents, CI/CD pipeline configs, deployment runbooks, or any documentation mentioning backup, recovery, or contingency planning |
| sf-experience-cloud-security | Experience Cloud site metadata, Guest User profile XML, Network member configuration, or design documents mentioning Experience Cloud, Community, or guest user access |
| sf-package-review        | sfdx-project.json with `packageDirectories` or `packageAliases`, or any metadata organized in a 1GP/2GP/unlocked package structure |

Only load a skill file if the condition in that row is met.

---

## STEP 2 — Static analysis

Only if: .cls, .trigger, .js, or .html files are in the inventory.

Load skill: #file:.github/skills/sf-static-analysis/SKILL.md

Engine selection is automatic — the scanner runs all applicable engines based on file types. See the skill file for single-command execution, CSV output, column mapping, and merge protocol.

Execution requirements:

- Run SF Code Analyzer using `--format csv --outfile` as specified in the skill file.
- Collect findings from the CSV output and mark each with `Type = code-analyzer` for CSV export.
- If an engine is not applicable, log: `Engine <name> — not applicable: no <file type> files in scope.`
- If an engine fails, log: `Engine <name> did not run — <error>` and add a corresponding CSV row.
- Never require human copy/paste of analyzer results when tools are installed and runnable.

---

## STEP 3 — Security review

Load skill: #file:.github/skills/sf-security/SKILL.md

---

## STEP 4 — Architecture and over-engineering

Only if: Apex triggers, Flows, handler classes, batch/async, or integration code detected.

Load skill: #file:.github/skills/sf-architecture/SKILL.md

This step covers both architecture patterns AND over-engineering signals. Evaluate all sections of the skill including:

- Automation density assessment
- Trigger framework
- Service / selector / domain layer
- Apex design patterns
- Integration patterns
- Batch and async patterns
- Flow and automation
- **Over-engineering signals** — flag each with `[OVER-ENGINEERING]` in findings

---

## STEP 5 — Data model

Load skill: #file:.github/skills/sf-data-model/SKILL.md

---

## STEP 6 — Governor limits and performance

Only if: Apex triggers, batch, queueable, Flows, or SOQL-heavy classes detected.

Load skill: #file:.github/skills/sf-governor-performance/SKILL.md

This single step covers: automation conflict mapping, SOQL limits + selectivity, DML limits, CPU time risks, heap size risks, async limits, LDV patterns, report/dashboard performance, and Experience Cloud query patterns.

---

## STEP 7 — Test quality

Load skill: #file:.github/skills/sf-test-quality/SKILL.md

---

## STEP 8 — API versioning and deprecation

Load skill: #file:.github/skills/sf-api-versioning/SKILL.md

---

## STEP 9a — Build forms architecture and UX

Only if: Screen Flow, Dynamic Forms, Omnistudio, or form LWC detected.

Load skill: #file:.github/skills/sf-build-forms/SKILL.md

---

## STEP 9b — Event-driven architecture

Only if: Platform Events, CDC, Pub/Sub, or streaming patterns detected.

Load skill: #file:.github/skills/sf-event-driven/SKILL.md

---

## STEP 9c — Deployment and DevOps

Only if: package.xml, destructiveChanges.xml, CI/CD config, scratch org definition, or .forceignore detected.

Load skill: #file:.github/skills/sf-deployment/SKILL.md

---

## STEP 9d — Web application security

Only if: Visualforce pages, Apex controllers with `PageReference` or redirect logic, file upload Apex, static resource metadata, or LWC with CSP or `innerHTML` concerns detected.

Load skill: #file:.github/skills/sf-web-app-security/SKILL.md

---

## STEP 9e — Authentication and session security

Only if: connected app metadata, profile or permission set XML, or design documents mentioning authentication, MFA, session settings, or password policy are present.

Load skill: #file:.github/skills/sf-auth-session-security/SKILL.md

---

## STEP 9f — Shield Platform Encryption

Only if: permission set metadata with encryption permissions, Apex referencing encrypted fields, PII field design, or design documents mentioning Shield, HIPAA, or data encryption are present.

Load skill: #file:.github/skills/sf-shield-encryption/SKILL.md

---

## STEP 9g — Audit logging and monitoring

Only if: Apex querying `EventLogFile`, Transaction Security Policy metadata, or design documents mentioning HIPAA/MARS-E, event monitoring, or audit trail are present.

Load skill: #file:.github/skills/sf-audit-monitoring/SKILL.md

---

## STEP 9h — Resilience and recovery

Only if: design documents, CI/CD pipeline configs, deployment runbooks, or documentation mentioning backup, recovery, contingency planning, RTO, or RPO are present.

Load skill: #file:.github/skills/sf-resilience/SKILL.md

---

## STEP 9i — Experience Cloud security

Only if: Experience Cloud site metadata, Guest User profile XML, Network member configuration, or design documents mentioning Experience Cloud, Community, or guest user access are detected.

Load skill: #file:.github/skills/sf-experience-cloud-security/SKILL.md

---

## STEP 9j — Package review

Only if: `sfdx-project.json` with `packageDirectories` or `packageAliases`, or any metadata organized in a 1GP/2GP/unlocked package structure is detected.

Load skill: #file:.github/skills/sf-package-review/SKILL.md

---

## STEP 10 — Code quality: patterns, anti-patterns, and SOLID

Only if: any .cls, .trigger, .js, .html files, or Apex interfaces/abstract classes/handlers/services/selectors are in the inventory.

Load skill: #file:.github/skills/sf-code-quality/SKILL.md

Review in a single pass:

- Bulkification violations (SOQL/DML in loops, per-record async enqueue)
- Hardcoding (record IDs, profile IDs, org-specific values)
- God class / mixed-responsibility class signals
- Static variable abuse
- Null and error handling failures
- LWC-specific anti-patterns
- Flow loop and DML anti-patterns
- **SOLID principles**: SRP, OCP, LSP, ISP, DIP

Tag each SOLID finding with the violated principle: `[SRP]`, `[OCP]`, `[LSP]`, `[ISP]`, `[DIP]`.

**Note**: Bulkification and async-limit checks overlap with Step 6. When writing CSV, deduplicate by `(Component, Category, Issue, Location)` — keep the higher severity.

---

## STEP 11 — Review report and CSV export

### Executive summary

| Metric                          | Count |
| ------------------------------- | ----- |
| Components reviewed             |       |
| Critical findings               |       |
| High findings                   |       |
| Medium findings                 |       |
| Low / informational             |       |
| Over-engineering flags          |       |
| Data model violations           |       |
| Security findings               |       |
| Performance findings            |       |
| Forms findings                  |       |
| Event-driven findings           |       |
| Code quality findings           |       |
| SOLID violations                |       |
| Web app security findings       |       |
| Auth / session security findings|       |
| Shield encryption findings      |       |
| Audit / monitoring findings     |       |
| Resilience findings             |       |
| Experience Cloud security findings |    |
| Package review findings         |       |

### Findings table

| #   | Component | Type | Severity | Category | Issue | Location | Reference | Suggestion |
| --- | --------- | ---- | -------- | -------- | ----- | -------- | --------- | ---------- |

**Severity**: Critical · High · Medium · Low · Info

**Category**: Security · Governor Limits · Performance · Apex Pattern · Anti-Pattern · Over-Engineering · Data Model · Test Quality · Automation Conflict · Deployment · LWC · Integration · Architecture · API Versioning · Forms · Event-Driven · **SOLID-SRP** · **SOLID-OCP** · **SOLID-LSP** · **SOLID-ISP** · **SOLID-DIP** · Web-App-Security · Auth-Session · Shield-Encryption · Audit-Monitoring · Resilience · Experience-Cloud-Security · Package-Review

### What passes review

List components and specific patterns that are correctly implemented. Be precise — no generic praise.

### Clarifications needed

List anything that could not be assessed due to missing context. State exactly what additional input would allow assessment.

### Skills not applicable to this review

| Skill | Reason skipped |
| ----- | -------------- |

### CSV export

Generate a CSV file containing all findings in a structured format.

- **Filename**: `genie-review-findings-[YYYYMMDD-HHMMSS].csv`
- **Location**: `Code Review Findings/` folder in the workspace root (created automatically if not present)
- **Columns**: Component, Type, Severity, Category, Issue, Location, Reference, Suggestion
- **Rows**: One row per finding from all applicable review steps

Merge requirements:

- Merge findings from both sources in a single CSV:
  - `agent-review` (manual review workflow findings)
  - `code-analyzer` (SF Code Analyzer findings from STEP 2)
- Deduplicate rows by `(Component, Category, Issue, Location)` before write. Keep higher severity on duplicates.
- **Category alignment for deduplication**: When `sf-security` and `sf-code-quality` both flag the same hardcoded ID or credential at the same location, treat Category = Security and Category = Anti-Pattern as the same finding — retain the higher severity and use Category = Security.
- Verify CSV file exists after writing. If not present, treat review as incomplete.

### Brief summary output

After generating the CSV file, output ONLY:

- 1–3 sentence summary of the review
- CSV file path
- Total row count
- Split counts: `agent-review` findings vs `code-analyzer` findings

Never paste the full CSV content in chat unless the user explicitly asks.

1. **Header**: "Review Complete"
2. **Summary (2–3 sentences)**: State the number of components reviewed, total findings, and link to CSV file.
3. **CSV file path**: Full relative path to generated CSV (e.g., `Code Review Findings/genie-review-findings-20260416-143022.csv`)
4. **Metrics**: Include counts of each severity level (Critical, High, Medium, Low, Info)
5. **Source split**: Include counts for `agent-review` and `code-analyzer`

**Example output format:**

```
Review Complete

Reviewed 3 Salesforce components across Apex, LWC, and deployment configuration.
Found 12 total findings: 1 Critical, 3 High, 5 Medium, 3 Low.
Full details exported to Code Review Findings/genie-review-findings-20260416-143022.csv.

Critical: 1 | High: 3 | Medium: 5 | Low: 3 | Info: 0
Source split: agent-review: 4 | code-analyzer: 8
```

**Note**: Do NOT include the full findings table in the chat output. All findings are in the CSV file.
