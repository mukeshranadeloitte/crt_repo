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

**Do not run any install command until the developer answers Yes.**

If approved — install in this order:

1. If Node.js is missing: direct the developer to https://nodejs.org and pause.
2. If Salesforce CLI is missing: `npm install --global @salesforce/cli`
3. If Code Analyzer plugin is missing: `sf plugins install @salesforce/sfdx-scanner`

If the developer answers No — state the manual install commands and halt. Do not proceed with review until tools are confirmed installed.

**Do not proceed past this step if tools are not confirmed installed.**

---

## STEP 1 — Input detection and component inventory

Accept these input types (detect automatically): single file, list of files, `package.xml`, design document, GitHub link.

Produce a component inventory before any analysis. Based only on what is in the input — no assumptions.

| Component | Type | Apparent purpose |
| --------- | ---- | ---------------- |

If only a design document is provided with no source code, state that static analysis cannot run and scope to architecture and data model only.

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
| sf-auth-session-security | Connected app metadata, Profile or Permission Set XML, design docs mentioning authentication, MFA, session settings, or password policy |
| sf-shield-encryption     | Permission set metadata with encryption permissions, Apex referencing encrypted fields, or design docs mentioning Shield, PII fields, or HIPAA |
| sf-audit-monitoring      | Apex querying `EventLogFile`, Transaction Security Policy metadata, design docs mentioning HIPAA/MARS-E, event monitoring, or audit trail |
| sf-resilience            | Design docs, CI/CD pipeline configs, deployment runbooks, or documentation mentioning backup, recovery, or contingency planning |
| sf-experience-cloud-security | Experience Cloud site metadata, Guest User profile XML, Network member config, or design docs mentioning Experience Cloud, Community, or guest user access |
| sf-package-review        | sfdx-project.json with `packageDirectories` or `packageAliases`, or metadata organized in a 1GP/2GP/unlocked package structure |

Only load a skill file if the condition in that row is met.

---

## STEP 2 — Static analysis

Only if: .cls, .trigger, .js, or .html files are in the inventory.

Load skill: #file:.github/skills/sf-static-analysis/SKILL.md

Run SF Code Analyzer using `--format csv --outfile` as specified in the skill file. Collect findings and mark each with `Type = code-analyzer` for CSV export.

---

## STEP 3 — Security review

Load skill: #file:.github/skills/sf-security/SKILL.md

---

## STEP 4 — Architecture and over-engineering

Only if: Apex triggers, Flows, handler classes, batch/async, or integration code detected.

Load skill: #file:.github/skills/sf-architecture/SKILL.md

---

## STEP 5 — Data model

Load skill: #file:.github/skills/sf-data-model/SKILL.md

---

## STEP 6 — Governor limits and performance

Only if: Apex triggers, batch, queueable, Flows, or SOQL-heavy classes detected.

Load skill: #file:.github/skills/sf-governor-performance/SKILL.md

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

Only if: Visualforce pages, Apex with `PageReference` or redirect logic, file upload Apex, static resource metadata, or LWC with CSP or `innerHTML` concerns detected.

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

Review in a single pass: bulkification violations, hardcoding, God class signals, static variable abuse, null/error handling failures, LWC anti-patterns, Flow loop/DML anti-patterns, and SOLID principles (SRP, OCP, LSP, ISP, DIP). Tag each SOLID finding: `[SRP]`, `[OCP]`, `[LSP]`, `[ISP]`, `[DIP]`.

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

### CSV export

Generate a CSV file: `Code Review Findings/genie-review-findings-[YYYYMMDD-HHMMSS].csv`

Columns: Component, Type, Severity, Category, Issue, Location, Reference, Suggestion

- Merge `agent-review` and `code-analyzer` findings in one CSV.
- Deduplicate by `(Component, Category, Issue, Location)` — keep higher severity.
- Verify CSV file exists after writing. If not present, treat review as incomplete.

### Brief summary output (in chat)

Output only:
- 1–3 sentence summary
- CSV file path
- Total row count + split: `agent-review` vs `code-analyzer`

Never paste the full CSV content in chat unless the user explicitly asks.
