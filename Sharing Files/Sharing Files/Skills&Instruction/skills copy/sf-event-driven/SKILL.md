---
name: sf-event-driven
description: "Use when reviewing Salesforce event-driven architecture choices, Platform Events, Change Data Capture, Pub/Sub API, event relays, queuing and streaming patterns, and event anti-patterns. Trigger phrases: event-driven review, platform events review, CDC review, pub/sub review, event relay review, queueing pattern review, streaming pattern review."
---

Review against the Salesforce Architect decision guide for event-driven architecture. Only flag what is observable in the input. Do not fetch any external URLs.

## Suitability checks

| Check                                                                                          | Severity |
| ---------------------------------------------------------------------------------------------- | -------- |
| Event-driven pattern selected for synchronous user-waiting process                             | High     |
| Event-driven pattern used where source data changes infrequently and batch pattern is adequate | Medium   |
| No documented business reason for near-real-time/fanout/streaming behavior                     | Medium   |

## Tooling and product selection checks

| Check                                                                                                        | Severity |
| ------------------------------------------------------------------------------------------------------------ | -------- |
| New publish/subscribe implementation uses Streaming API, PushTopic, or generic events instead of Pub/Sub API | High     |
| CDC or Platform Events use case implemented via custom polling APIs with no rationale                        | High     |
| Event relay assumed for non-AWS target though Event Relays only support Amazon EventBridge                   | High     |
| Existing MuleSoft/ESB landscape ignored and duplicate custom event bus built in Salesforce                   | Medium   |

## Pattern-level design checks

| Pattern           | Required characteristic                                            | Finding if violated                                                     | Severity |
| ----------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------- | -------- |
| Publish/Subscribe | Publisher and subscriber are loosely coupled via event bus         | Direct point-to-point coupling masquerading as event-driven             | High     |
| Streaming         | Ordered per-subscriber event processing design                     | No ordering strategy when events originate from multiple systems        | High     |
| Queuing           | Delivery durability and queue retention strategy                   | No queue purge/backpressure plan for offline subscribers                | High     |
| Passed Messages   | Transformation pipeline segmented into dedicated components        | Monolithic transform handler for high-volume transformations            | Medium   |
| Fanout            | Single message fanout to many subscribers with delivery monitoring | No subscriber delivery verification strategy for critical notifications | High     |

## Event anti-pattern checks

| Check                                                                                                     | Severity |
| --------------------------------------------------------------------------------------------------------- | -------- |
| Platform Event published from Apex trigger on same event object (trigger loop risk)                       | Critical |
| Publish Immediately behavior used for business-critical transactional event without rollback-safe design  | High     |
| Events used to orchestrate intra-org Flow logic instead of Subflows/Flow Orchestrator                     | Medium   |
| Runtime package dependency created through event contracts with no versioning strategy                    | High     |
| Oversized event payloads with unnecessary fields                                                          | Medium   |
| Bidirectional event echo loop risk (systems republish each other's updates) without loop-prevention guard | Critical |

Source: Salesforce Developer Guide — Platform Events — Limits and Allocations

## Governance and versioning checks

| Check                                                               | Severity |
| ------------------------------------------------------------------- | -------- |
| No event schema ownership/governance process documented             | High     |
| No versioning lifecycle for event schema changes                    | High     |
| No replay/failure recovery strategy for critical subscribers        | High     |
| No naming convention standard for event channels and payload fields | Medium   |

## Operational resilience checks

| Check                                                           | Severity |
| --------------------------------------------------------------- | -------- |
| No dead-letter or retry strategy for failed event consumption   | High     |
| No monitoring for backlog/throughput/event bus bottlenecks      | High     |
| No allocation analysis for event volume against platform limits | High     |

Source: Salesforce Architect — Event-Driven Architecture Decision Guide
