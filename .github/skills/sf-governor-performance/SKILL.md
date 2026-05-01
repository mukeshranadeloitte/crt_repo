---
name: sf-governor-performance
description: "Use when reviewing Salesforce governor limits and performance: SOQL/DML counts, CPU time, heap size, async limits, automation conflicts, SOQL selectivity, large data volumes, collection patterns, Experience Cloud queries. Trigger phrases: governor limits, DML limit, SOQL limit, CPU limit, heap, automation conflict, performance, large data volume, LDV, selectivity, index."
---

Only flag what is observable in the input. Every finding must cite a Salesforce source. This skill consolidates governor-limit and performance checks into a single pass.

---

## Automation conflict mapping

For every object in scope, map all active automation:

| Object | Triggers | Record-Triggered Flows | Process Builders (legacy) | Workflow Rules (legacy) | Validation Rules |
| ------ | -------- | ---------------------- | ------------------------- | ----------------------- | ---------------- |

Flag:

- Objects where Trigger + Flow + Process Builder all fire on the same event — execution order is unpredictable (High)
- Validation rules that duplicate logic already enforced in Apex — dual enforcement creates maintenance risk (Medium)
- Process Builder or Workflow Rules still active on objects that have record-triggered flows — migrate to Flow (Medium)

Source: Apex Developer Guide — Order of Execution

---

## SOQL limits and selectivity (combined)

| Check | Severity |
| ----- | -------- |
| SOQL query inside a `for` loop | Critical |
| SOQL inside `for` loop over a collection | Critical |
| Estimated SOQL queries ≥ 80 per transaction | High — limit is 100 |
| Subquery depth > 1 level | Medium |
| SOQL on non-selective filters on large objects (>100K records) | High |
| SOQL WHERE clause uses leading wildcard (`LIKE '%value'`) | High — full table scan |
| SOQL WHERE clause filters on a non-indexed field on an object expected to exceed 100K records | High |
| SOQL WHERE clause has no filter at all on a high-volume object | High |
| `offset` used with value > 2000 in queries on large objects | Medium |
| SOQL `ORDER BY` on a non-indexed field on a large object | Medium |
| Cross-object formula field used in a SOQL WHERE clause — not indexed | Medium |

Selective filter threshold: result set < 10% of total records OR < 333K records (whichever is smaller).

Source: Apex Developer Guide — Execution Governors and Limits · Salesforce SOQL and SOSL Reference — Query Optimization

---

## SOSL limits

| Check | Severity |
| ----- | -------- |
| SOSL query inside a `for` loop | Critical |
| Estimated SOSL queries ≥ 18 per transaction | High — limit is 20 |
| SOSL `FIND` clause uses a single leading wildcard (`FIND '*value'`) — full-text index not used | High |
| SOSL `RETURNING` clause queries 5+ objects in a single statement without documented justification | Medium |
| SOSL used on objects where SOQL with a selective filter would be more predictable and performant | Medium |
| SOSL result set iterated without a LIMIT — unbounded result risk on large text-search targets | High |

Source: Apex Developer Guide — Execution Governors and Limits · Salesforce SOQL and SOSL Reference — SOSL Queries

---

## DML limits

| Check | Severity |
| ----- | -------- |
| DML statement inside a `for` loop | Critical |
| DML inside a `@future` called in a loop | Critical |
| Estimated DML statements ≥ 140 per transaction | High — limit is 150 |
| Recursive DML without a recursion guard (static flag or trigger handler) | High |

Source: Apex Developer Guide — Execution Governors and Limits

---

## CPU time risks

| Check | Severity |
| ----- | -------- |
| Nested loops (O(n²)) over collections derived from SOQL | High |
| String concatenation (`+=`) inside a loop — use `List<String>` + `String.join` | Medium |
| `JSON.serialize` / `JSON.deserialize` inside a loop | Medium |
| Unguarded recursion in trigger or flow chain | High |
| `Schema.getGlobalDescribe` called inside a loop or without caching | High |
| `Schema.describeSObjects` called in a loop | High |
| `Map.containsKey` inside a loop where a pre-built Map would eliminate redundant lookups | Medium |
| Regular expression (`Pattern.compile`) called inside a loop — compile once outside | Medium |

Source: Apex Developer Guide — Execution Governors and Limits

---

## Heap size risks

| Check | Severity |
| ----- | -------- |
| Full SOQL result set materialized into a `List` without a `LIMIT` clause | High |
| Static List/Map accumulating across batch chunks without reset | High |
| Large JSON payloads deserialized into generic Object collections | Medium |
| `List` or `Map` built inside a loop from another collection (O(n) allocation) | Medium |
| `String +=` concatenation inside a loop (heap fragmentation) | Medium |

Source: Apex Developer Guide — Execution Governors and Limits

---

## Async limits

| Check | Severity |
| ----- | -------- |
| `@future` method called inside a loop | Critical |
| `Database.executeBatch` called inside a trigger context | Critical — not designed for trigger invocation |
| `System.schedule` called inside a trigger context | Critical — not designed for trigger invocation |
| `System.enqueueJob` called inside a loop | High |
| `System.enqueueJob` called without checking `Limits.getQueueableJobs() < Limits.getLimitQueueableJobs()` | High |
| Queueable enqueued from trigger without detecting async context via `System.isBatch()` | Critical — only 1 queueable from batch; up to 50 from sync |
| More than 50 queueable jobs enqueued in a single synchronous transaction without guard | High |
| Per-record async job enqueued in a bulk trigger with no batching strategy | Critical — consumes shared daily async limit |

**Daily async Apex execution limit**: 250,000 or (200 × number of user licenses), whichever is greater. Org-wide, shared across all Batch, Queueable, and @future.

Source: Apex Developer Guide — Execution Governors and Limits · Salesforce Record-Triggered Automation — Async Limits

---

## Large data volume (LDV) patterns

| Check | Severity |
| ----- | -------- |
| Batch class `scope` size not set — defaults to 200, may be too large for LDV with complex triggers | Medium |
| No skinny table consideration for objects expected to reach millions of records | Medium |
| Master-Detail on object likely to exceed 10M child records — roll-up recalculation risk | High |
| Sharing recalculation not considered for LDV objects with complex sharing rules | High |
| `Database.QueryLocator` not used in batch start for queries returning >50K records | High |

Source: Salesforce Large Data Volumes Developer Guide

---

## Report and dashboard performance

| Check | Severity |
| ----- | -------- |
| Report on a high-volume object with no date range filter | High |
| Report joined across 4+ objects | Medium |
| Dashboard component sources a real-time report on a high-volume object | Medium |

Source: Salesforce Help — Report Builder Performance Best Practices

---

## Experience Cloud / Guest user query patterns

| Check | Severity |
| ----- | -------- |
| Wire adapter or Apex method called on page load with no filter — full object query for guest users | High |
| Unauthenticated page loads trigger SOQL on Contact, Lead, or Account without selective filter | High |

Source: Salesforce Help — Experience Cloud Performance Guide
