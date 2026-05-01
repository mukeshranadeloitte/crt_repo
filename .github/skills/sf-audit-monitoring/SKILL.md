---
name: sf-audit-monitoring
description: "Use when reviewing Salesforce audit logging, event monitoring, transaction security policies, HIPAA/MARS-E 2.0 compliance, Field Audit Trail, and anomaly detection configuration. Trigger phrases: audit logging, event monitoring, transaction security, HIPAA logging, MARS-E, field history, audit trail, anomaly detection, Field Audit Trail, EventLogFile, transaction security policy."
---

Review against Salesforce Event Monitoring documentation, MARS-E 2.0, and HIPAA audit control requirements. Only flag what is observable in the input — Apex classes, Transaction Security Policy metadata, Event Monitoring configuration, permission set XML, or design documents. Do not fetch any external URLs.

---

## Audit logging configuration

| Check | Severity |
| ----- | -------- |
| Design document does not reference Event Monitoring or EventLogFile consumption for a HIPAA- or MARS-E-scoped org | Critical |
| Apex code uses `System.debug` as the sole audit trail for privileged or sensitive operations | High |
| No custom log object, Platform Event, or external SIEM integration documented for security event capture | High |
| `EventLogFile` object not queried, forwarded, or referenced in any Apex, integration, or design documentation | Medium |
| Design document does not identify which event log types are required per MARS-E 2.0 AU-2 (login, logout, data access, export events) | High |

Source: Salesforce Event Monitoring Developer Guide · MARS-E 2.0 — AU-2, AU-3

---

## Audit log retention

| Check | Severity |
| ----- | -------- |
| Design document does not specify a 10-year (or regulation-required) audit log retention period | High |
| Field Audit Trail not referenced in design for objects storing PII, financial, or regulated data | High |
| Field History Tracking used as the primary long-term retention mechanism — native limit is 18 months without Field Audit Trail | High |
| No external archival strategy documented for Event Log Files — default platform retention is 30 days for standard orgs | Critical |
| EventLogFile archival to an external system not automated (manual export is documented as the only method) | High |

Source: Salesforce Help — Field Audit Trail · MARS-E 2.0 — AU-11

---

## Audit log access restrictions

| Check | Severity |
| ----- | -------- |
| Apex class querying `EventLogFile` or audit trail objects does not declare `with sharing` | High |
| Permission set granting access to `EventLogFile`, Field Audit Trail, or audit-related objects is assigned broadly or to non-privileged users | High |
| No documented role-based access control for audit log retrieval and export | High |
| Design document does not specify the authorized user list for audit log access | Medium |
| `EventLogFile` data exposed via an `@AuraEnabled` or REST endpoint without FLS enforcement | High |

Source: Salesforce Event Monitoring — Access and Setup · MARS-E 2.0 — AU-9

---

## Transaction security policies

| Check | Severity |
| ----- | -------- |
| Design document does not reference Transaction Security Policies for a HIPAA- or MARS-E-regulated org | High |
| No Transaction Security Policy defined or referenced for anomalous login behavior (e.g. impossible travel, unexpected IP) | Critical |
| No Transaction Security Policy defined for bulk data export events (e.g. `ReportEvent`, `DataExport`) | Critical |
| Transaction Security Policy metadata is present but `actionConfig` specifies `NoAction` or is empty | High |
| Policy scope covers only one event type when multiple high-risk event types exist in the org | High |

Source: Salesforce Help — Transaction Security Policies · MARS-E 2.0 — SI-4

---

## Custom security policy actions

| Check | Severity |
| ----- | -------- |
| Transaction Security Policy `actionConfig` does not specify Block, MFA Challenge, or End Session for high-risk events | High |
| No notification action configured for critical policy trigger events (no email, in-app alert, or Platform Event) | Medium |
| Bulk export policy action configured to notify only — no blocking action for anomalous volume | High |
| Apex-based Transaction Security Policy action handler does not implement error handling or event logging for triggered events | Medium |
| Policy action Apex class does not declare `with sharing` | High |

Source: Salesforce Help — Transaction Security Policies — Custom Apex Actions · MARS-E 2.0 — IR-4
