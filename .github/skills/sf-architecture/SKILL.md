---
name: sf-architecture
description: "Use when reviewing Salesforce architecture patterns, trigger frameworks, service/selector/domain layers, integration patterns, batch/async patterns, Flow automation, and over-engineering signals. Trigger phrases: architecture review, trigger framework, handler pattern, service layer, selector, domain layer, fflib, integration pattern, batch, queueable, flow pattern, over-engineering."
---

Review against the Salesforce Well-Architected Framework and the Record-Triggered Automation Decision Guide. Only flag what is observable in the input. Do not fetch any external URLs.

## Automation density assessment

Count all active automation entries per object (triggers, flows, process builders). Classify and flag mismatches:

| Density | Threshold                                                                                              | Expected pattern                            | Flag if different |
| ------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------- | ----------------- |
| Low     | < 15 automations, standard UI/API loads (1–200 records), 0–1 downstream DML                            | Record-Triggered Flow only                  | High              |
| Medium  | 15–30 automations, moderate batch, 2–4 downstream DML, recursion risk                                  | Hybrid: Flow orchestration + Invocable Apex | High              |
| High    | > 30 automations, bulk API loads (2,000–10,000+ records), 5+ downstream DML, triangular recursion risk | Apex Trigger + Metadata Framework           | High              |

Flag **mixing Flow and Apex triggers as independent entry points on the same object** as High regardless of density.

Source: Salesforce Record-Triggered Automation Decision Guide — Density Selection Matrix

## Trigger framework

| Anti-pattern                                                                                                                               | Severity                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| Multiple triggers on the same object                                                                                                       | High                                                                 |
| Business logic directly in trigger body (not delegated to handler)                                                                         | High                                                                 |
| No handler class — no dispatcher, no interface                                                                                             | High                                                                 |
| Trigger calls DML that fires another trigger without a recursion guard                                                                     | High                                                                 |
| Recursion guard implemented via static boolean flag — prefer `Trigger.new` vs `Trigger.oldMap` field comparison (idempotent, more precise) | Medium                                                               |
| Classic monolithic handler class with no modular atomic classes                                                                            | Medium — recommend metadata-driven framework for medium/high density |
| Metadata-driven framework absent on a high-density object (>30 automations)                                                                | High                                                                 |
| No bypass mechanism — no custom permission check in trigger or flow entry criteria                                                         | Medium                                                               |
| Bypass implemented via hardcoded profile ID or user ID instead of Custom Permission                                                        | Medium                                                               |

Pattern: one trigger per object → `MetadataTriggerHandler` reads `TriggerAction__mdt` → executes atomic handler classes in declared order. Bypass via `FeatureManagement.checkPermission()`.

Source: Salesforce Record-Triggered Automation — Metadata Framework

## Custom Permission governance

| Check | Severity |
| ----- | -------- |
| Trigger or flow bypass logic uses a hardcoded Profile name, Profile ID, or User ID instead of `FeatureManagement.checkPermission()` with a Custom Permission | High |
| Multiple triggers or flows use inconsistent bypass mechanisms — no unified bypass strategy documented | Medium |
| Custom Permission used for feature flagging but no permission set assignment process or documentation exists | Medium |
| `FeatureManagement.checkPermission()` called inside a loop — result not cached per transaction | Medium |
| Feature flag logic embedded in Apex conditionals instead of a Custom Metadata record-driven dispatcher — cannot be toggled without a deployment | Medium |

Source: Salesforce Help — Custom Permissions · Apex Developer Guide — FeatureManagement

## Service / selector / domain layer

| Anti-pattern                                                               | Severity |
| -------------------------------------------------------------------------- | -------- |
| SOQL in Apex controllers or batch `execute`                                | Medium   |
| SOQL in Flow Get Records called from a trigger context without selectivity | Medium   |
| DML inside a selector class                                                | High     |
| Business logic duplicated across multiple service classes                  | Medium   |
| No separation between query construction and business logic                | Medium   |

Source: Apex Enterprise Patterns — Service / Selector / Domain Layer

## Apex design patterns

| Signal                                                                                  | Severity                  |
| --------------------------------------------------------------------------------------- | ------------------------- |
| if/else or switch chains with 5+ branches where a Strategy or Factory would apply       | Medium                    |
| `new ConcreteClass()` instantiation where a factory interface would improve testability | Low                       |
| Static variables accumulating org-wide state across transactions (Singleton abuse)      | High                      |
| Factory that instantiates only one class                                                | Medium (Over-Engineering) |
| Strategy with only one implementation                                                   | Medium (Over-Engineering) |
| Observer/Event pattern with a single subscriber                                         | Low (Over-Engineering)    |

## Integration patterns

| Anti-pattern                                                 | Severity |
| ------------------------------------------------------------ | -------- |
| Synchronous callout in a trigger or batch `execute`          | Critical |
| No retry or idempotency mechanism on outbound integrations   | High     |
| Async decoupling clearly needed but Platform Events not used | Medium   |
| Hardcoded endpoint URL — Named Credential not used           | High     |
| No response validation on HTTP callout                       | High     |

Source: Salesforce Integration Patterns and Practices

## Batch and async patterns

| Anti-pattern                                                                                             | Severity                                                                                |
| -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Batch class accumulates state but does not implement `Database.Stateful`                                 | High                                                                                    |
| Queueable chain with no depth limit (infinite recursion risk)                                            | High                                                                                    |
| `@future` method called inside a loop                                                                    | High                                                                                    |
| Scheduled job without error notification or alerting mechanism                                           | Medium                                                                                  |
| `Database.executeBatch` or `System.schedule` called directly from trigger context                        | Critical                                                                                |
| `System.enqueueJob` called without checking `Limits.getQueueableJobs() < Limits.getLimitQueueableJobs()` | High                                                                                    |
| Queueable called from trigger without detecting async context via `System.isBatch()`                     | High                                                                                    |
| Queueable or @future enqueued per-record in a bulk trigger (200 records = 200 jobs) without batching     | Critical                                                                                |

Async pattern selection order: Flow async path → CDC → Queueable Apex → Scheduled Job pattern.

Source: Salesforce Record-Triggered Automation — Async Patterns

## Flow and automation

| Anti-pattern                                                                                                                  | Severity                                                                                 |
| ----------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Record-triggered flow with no entry conditions (fires on every save)                                                          | High                                                                                     |
| Multiple flows on same object + same trigger event without Flow Trigger Explorer ordering configured                          | High                                                                                     |
| Flow calls Apex Invocable Action without considering bulk-safe invocation                                                     | High                                                                                     |
| Invocable Apex action called from a **before-save** flow context                                                              | Critical — Invocable Actions are only supported in after-save context                    |
| Flow used for after-undelete business logic — Flow does not support after-undelete context; Apex trigger required             | High                                                                                     |
| Single mega-flow containing all automation for an object                                                                      | Medium                                                                                   |
| After-save flow used for same-record field updates where a before-save flow would suffice                                     | Medium                                                                                   |
| Sub-flow used once with no documented reuse justification                                                                     | Low (Over-Engineering)                                                                   |
| Process Builder still active on objects that have record-triggered flows                                                      | High (deprecated; migrate to Flow)                                                       |
| Recursion prevented via Flow entry condition `Always` instead of `Only when record is updated to meet condition requirements` | High                                                                                     |
| Flow entry condition does not compare `$Record` vs `$RecordPrior` for field-change-specific logic                             | Medium                                                                                   |

Source: Salesforce Record-Triggered Automation Decision Guide · Flow Best Practices (Salesforce Help)

## Process Builder migration assessment

| Check | Severity |
| ----- | -------- |
| Active Process Builder on an object that already has a record-triggered Flow — dual execution risk | High |
| Process Builder containing Apex invocations — migration to Flow requires equivalent Invocable Actions | Medium |
| More than 3 active Process Builders on the same object — migration sequencing required | Medium |
| No documented migration roadmap for active Process Builders despite platform retirement | High |

Source: Salesforce Help — Process Builder Retirement · Salesforce Record-Triggered Automation Decision Guide

## Over-engineering signals

Every flag must cite a specific observable symptom. Flag as **[OVER-ENGINEERING]**.

| Signal                                                                                                                     | Severity |
| -------------------------------------------------------------------------------------------------------------------------- | -------- |
| Custom logging framework where Platform Event + Big Object would suffice                                                   | Medium   |
| Custom retry logic where a Queueable with counter would suffice                                                            | Medium   |
| Abstract class hierarchy deeper than 2 levels for a single object                                                          | High     |
| `Type.forName` or dynamic describe loops where direct references would work and no extensibility requirement is documented | Medium   |
| Custom Metadata used for logic that changes once a year, maintained by developers not admins                               | Medium   |
| 10+ small classes for a workflow involving 2–3 objects and a single trigger event                                          | High     |

Source: Salesforce Well-Architected — Adaptable
