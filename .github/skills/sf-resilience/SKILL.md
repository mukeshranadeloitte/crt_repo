---
name: sf-resilience
description: "Use when reviewing Salesforce backup strategy, contingency planning, disaster recovery, rollback plans, and business continuity documentation. Trigger phrases: backup plan, contingency plan, disaster recovery, rollback plan, recovery plan, business continuity, data recovery, OwnBackup, RTO, RPO, restore procedure."
---

Review against MARS-E 2.0 contingency planning controls, NIST SP 800-34, and Salesforce backup documentation. Only flag what is observable in the input — design documents, CI/CD pipeline configurations, deployment runbooks, or metadata. Do not fetch any external URLs.

---

## Backup and contingency planning

| Check | Severity |
| ----- | -------- |
| Design document does not reference any data backup solution (e.g. OwnBackup, Spanning, Veeam, native Salesforce Weekly Export) | Critical |
| No backup frequency or retention period documented for the Salesforce org | High |
| Backup solution scope does not cover all custom objects containing PII, regulated, or business-critical data | High |
| No documented or tested restore procedure for recovering Salesforce data from backup | Critical |
| No contingency plan or Business Continuity Plan referenced for the Salesforce org | Critical |
| Recovery Time Objective (RTO) and Recovery Point Objective (RPO) not defined in design documentation | High |
| Backup access not restricted to authorized personnel — no role or permission restriction documented | High |

Source: Salesforce Help — Data Backup and Recovery · MARS-E 2.0 — CP-9, CP-10 · NIST SP 800-34

---

## Rollback and recovery planning

| Check | Severity |
| ----- | -------- |
| Deployment pipeline has no documented rollback procedure (e.g. sandbox point-in-time restore, `destructiveChanges.xml` revert, version control revert) | High |
| Rollback plan would expose production data in a sandbox environment without documented data masking | Critical |
| No documented owner or runbook responsible for executing the rollback plan | Medium |
| Rollback plan has not been reviewed or tested within the last release cycle | High |
| CI/CD pipeline has no health check or smoke test step to trigger automated rollback on deployment failure | Medium |

Source: Salesforce DX Developer Guide — Sandboxes and Rollback · MARS-E 2.0 — CP-12
