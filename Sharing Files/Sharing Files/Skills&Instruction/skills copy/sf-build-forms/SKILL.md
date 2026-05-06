---
name: sf-build-forms
description: "Use when reviewing Salesforce form architecture and implementation choices across Dynamic Forms, Screen Flow, Omnistudio, and LWC. Trigger phrases: build forms review, form architecture review, screen flow form review, omnistudio form review, LWC form UX review, dynamic forms review."
---

Review against the Salesforce Architect decision guide for forms. Only flag what is observable in the input. Do not fetch any external URLs.

## Tool selection fit

| Observable scenario                                                      | Preferred tool                   | Finding if violated                                     | Severity                  |
| ------------------------------------------------------------------------ | -------------------------------- | ------------------------------------------------------- | ------------------------- |
| Single-object create/edit/view on Lightning record page with standard UX | Dynamic Forms                    | LWC or complex Flow used without clear requirement      | Medium (Over-Engineering) |
| Multi-screen or wizard workflow without strict branding requirements     | Screen Flow                      | Custom LWC navigation framework built unnecessarily     | Medium                    |
| Medium complexity form with complex compute/logic in some steps          | Screen Flow + Invocable Apex/LWC | All logic hardcoded in one LWC without reuse rationale  | Medium                    |
| Pixel-perfect branding, complex hierarchical data, Industries context    | Omnistudio or LWC                | Dynamic Forms chosen despite unmet UX/data requirements | High                      |

## Navigation and form scope checks

| Check                                                                                         | Severity |
| --------------------------------------------------------------------------------------------- | -------- |
| Multi-step process implemented with Dynamic Forms only                                        | High     |
| Wizard process implemented in LWC without explicit need to replace native Flow navigation     | Medium   |
| Screen Flow used with heavy per-screen DML where commit-at-end would reduce partial-save risk | Medium   |
| Form requires jump navigation but Flow-only implementation chosen with no workaround          | Medium   |

## Transaction and data integrity checks

| Check                                                                                                        | Severity |
| ------------------------------------------------------------------------------------------------------------ | -------- |
| External callout executed in same transaction after pending DML operations                                   | High     |
| Flow callout action not configured with transaction boundary where required (Always start a new transaction) | High     |
| Multi-record operation commits per-step when requirement implies all-or-none semantics                       | High     |
| Rollback requirement present but no Fault path + Roll Back Records design                                    | High     |

Source: Salesforce Help — Flows in Transactions

## Validation and interaction design checks

| Check                                                                                                               | Severity |
| ------------------------------------------------------------------------------------------------------------------- | -------- |
| Custom input component in Screen Flow has no validate() implementation                                              | High     |
| Required inputs are only validated server-side when client-side validation is feasible                              | Medium   |
| Dynamic required/read-only/disabled behavior needed but unsupported component used without LWC fallback             | Medium   |
| Reactive screen behavior needed but design relies on non-reactive manual variable/formula references on same screen | Medium   |

## Security checks for forms

| Check                                                                                                            | Severity |
| ---------------------------------------------------------------------------------------------------------------- | -------- |
| Screen Flow in System Context for guest users without strict field limitation in Get Records                     | Critical |
| System Context used broadly when user context is sufficient                                                      | High     |
| Rich text input from external/guest forms with no sanitization strategy                                          | High     |
| Access controls absent: flow exposed broadly with Run Flows permission and no profile/permission-set restriction | High     |
| LWC or Omniscript guest-exposed Apex actions missing explicit sharing and permission checks                      | Critical |

Source: Salesforce Help — Screen Flow Security

## Packaging and deployment checks

| Check                                                                                | Severity |
| ------------------------------------------------------------------------------------ | -------- |
| Omnistudio solution planned for package distribution (1GP/2GP/unlocked)              | High     |
| Omnistudio deployment planned via Change Sets/DevOps Center instead of IDX Workbench | High     |
| Form solution requires ISV packaging but relies on non-packageable Omnistudio assets | High     |

## Test and observability checks

| Check                                                                          | Severity |
| ------------------------------------------------------------------------------ | -------- |
| Form has non-trivial custom logic but no unit-testable LWC/Apex modules        | Medium   |
| No KPI instrumentation for completion rate / error rate on critical forms      | Medium   |
| Form architecture has no E2E automation plan despite high business criticality | Medium   |

Source: Salesforce Architect — Building Forms Decision Guide
