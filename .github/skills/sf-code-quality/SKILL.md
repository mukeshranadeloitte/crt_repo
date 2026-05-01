---
name: sf-code-quality
description: "Use when reviewing Salesforce Apex, LWC, and Flow code for design patterns, anti-patterns, code smells, SOLID principles, and Salesforce-specific bad practices. Trigger phrases: patterns review, anti-patterns, code smell, design pattern, bulkification, SOQL in loop, DML in loop, hardcoded ID, static variable abuse, God class, SOLID review, single responsibility, dependency injection."
---

Review against the Apex Developer Guide, Salesforce Well-Architected Framework, Apex Enterprise Patterns, and SOLID principles. Only flag what is observable in the input. Do not fetch any external URLs. This skill consolidates pattern/anti-pattern and SOLID checks into a single pass.

---

## Bulkification anti-patterns

| Anti-pattern | Severity | Reference |
| ------------ | -------- | --------- |
| SOQL query inside a `for` loop | Critical | Apex Best Practices — Bulkify |
| DML statement inside a `for` loop | Critical | Apex Best Practices — Bulkify |
| `@future` or `System.enqueueJob` called per record inside a loop | Critical | Async Apex Best Practices |
| `Trigger.new[0]` single-record assumption in trigger body | High | Triggers and Order of Execution |
| Callout made inside a loop | Critical | Callout Best Practices |
| `Database.query` (dynamic SOQL) constructed and executed inside a loop | Critical | Dynamic SOQL |

---

## Hardcoding anti-patterns

| Anti-pattern | Severity | Reference |
| ------------ | -------- | --------- |
| Hardcoded Salesforce Record ID (`001...`, `005...`, etc.) | High | Apex Security — Hardcoded IDs |
| Hardcoded Profile ID or Role ID | High | Permission Model Best Practices |
| Hardcoded org-specific value (email, URL, picklist value) with no Custom Metadata / Custom Setting fallback | Medium | 12-Factor Config |
| Hardcoded currency code or locale string | Medium | — |
| Hardcoded Record Type name without `Schema.SObjectType` lookup | Medium | Apex SObject Methods |

---

## God class / class responsibility (SRP violations)

| Anti-pattern | Severity | Reference |
| ------------ | -------- | --------- |
| Single class exceeds 500 lines with mixed responsibilities (query + logic + DML + UI formatting) | High | Clean Code — SRP |
| Controller performing SOQL, business logic, and callouts without delegation | High | Apex Enterprise Patterns — Service Layer |
| Utility class with 20+ unrelated static methods | Medium | — |
| Trigger handler class accumulates all object-level logic without domain decomposition (>300 lines) | High | Apex Enterprise Patterns — Domain Layer |
| LWC component manages data fetching, state transformation, and rendering logic without separation | Medium | — |
| Test class tests multiple unrelated concerns with no logical grouping | Low | — |

Tag finding: `[SRP]`

---

## Static variable abuse

| Anti-pattern | Severity | Reference |
| ------------ | -------- | --------- |
| Static `Map` or `List` used as a cross-transaction cache (static variables are per-request only) | High | Apex Developer Guide — Heap Size |
| Static boolean recursion guard set to `true` and never reset within the same transaction | High | Trigger Recursion Guard Patterns |
| Mutable static field used as shared state across Queueable chain links | High | — |

---

## Null / error handling anti-patterns

| Anti-pattern | Severity | Reference |
| ------------ | -------- | --------- |
| No null check before accessing fields on a queried SObject that may not exist | High | Apex Null Safety |
| Empty `catch` block that silently swallows exceptions | High | Exception Handling Best Practices |
| Catching `Exception` instead of the specific exception type | Medium | Apex Exceptions |
| `System.debug` used as the sole error signal (no platform logging, no custom log object) | Medium | — |
| No structured logging framework present — `System.debug` is the only observable logging pattern across the codebase with no Platform Event log, custom log object, or established logging library in use | High | Salesforce Well-Architected — Observable |
| `Database.SaveResult` or `Database.UpsertResult` checked without handling `isSuccess() == false` | High | Database Methods |

---

## LWC anti-patterns

| Anti-pattern | Severity | Reference |
| ------------ | -------- | --------- |
| `@wire` adapter result mutated directly (wire results are read-only) | High | LWC Wire Service |
| Imperative Apex called in `connectedCallback` without error handling | Medium | LWC Apex Calls |
| Parent-child communication via DOM event with no `composed: false` boundary consideration | Medium | LWC Event Propagation |
| CSS class toggling via direct DOM manipulation instead of reactive property binding | Medium | LWC Reactivity |
| `querySelectorAll` used to collect child component state instead of public `@api` method | Medium | LWC Component Communication |
| `window.setTimeout` used for polling instead of platform events or refresh apex | Medium | LWC Best Practices |

---

## Flow anti-patterns

| Anti-pattern | Severity | Reference |
| ------------ | -------- | --------- |
| Flow with no fault path on Get/Create/Update/Delete elements | High | Flow Best Practices |
| Loop inside a loop in a Flow (nested iteration without collection aggregation) | High | Flow Performance |
| DML element inside a Flow loop instead of collection-based Create/Update outside the loop | Critical | Salesforce Help — Flow Bulkification |
| Hard-coded label values in Flow decision conditions instead of Global Value Set or Custom Metadata | Medium | — |
| Screen Flow with no navigation validation before proceeding to next screen | Medium | Screen Flow UX |

---

## Cyclomatic complexity

Cyclomatic complexity counts the number of independent decision paths through a method. Flag when the observable method body exceeds the thresholds below.

| Check | Severity | Reference |
| ----- | -------- | --------- |
| Apex method with more than 10 distinct conditional branches (if, else if, switch when, logical and/or operators, ternary operators, catch blocks) | High | Salesforce Well-Architected — Reliable · Clean Code — Cyclomatic Complexity |
| Apex method with 15 or more distinct conditional branches — method must be decomposed | Critical | Clean Code — Cyclomatic Complexity |
| LWC JavaScript function with more than 8 distinct conditional branches — extract into helper functions | Medium | LWC Developer Guide — Best Practices |
| Flow with more than 10 decision outcomes in a single flow definition — split into sub-flows per responsibility | High | Salesforce Help — Flow Best Practices |
| Apex test method covers only one branch of a method with 10+ branches — branch coverage gap | Medium | Apex Testing Best Practices |

---

## SOLID — Open/Closed Principle (OCP)

| Violation | Severity | Signal |
| --------- | -------- | ------ |
| `if/else` or `switch` chain that must be modified to add new behavior (no Strategy, no metadata-driven dispatch) | High | 5+ branches on type/record-type/status |
| Trigger handler that requires editing the core handler class to add new actions | High | No `TriggerAction__mdt` or equivalent dispatch |
| Hardcoded conditional on Record Type where Custom Metadata could drive behavior | High | `if (rt.DeveloperName == 'TypeA')` |
| Flow that requires modifying the existing definition for new scenarios instead of sub-flows or invocable actions | Medium | Monolithic flow with embedded decision branches |

Tag finding: `[OCP]`

Source: Salesforce Developer Blog — Metadata Trigger Framework · Apex Enterprise Patterns

---

## SOLID — Liskov Substitution Principle (LSP)

| Violation | Severity | Signal |
| --------- | -------- | ------ |
| Subclass overrides a method and throws an exception the parent contract does not declare | High | `override` body has `throw new UnsupportedOperationException` |
| Interface implementation that silently ignores required method body (empty stub) | Medium | Interface method implemented as empty `{}` |
| `instanceof` used in business logic to differentiate subtype behavior | High | `if (obj instanceof SubclassA)` |

Tag finding: `[LSP]`

Source: Apex Developer Guide — Interfaces and Abstract Classes

---

## SOLID — Interface Segregation Principle (ISP)

| Violation | Severity | Signal |
| --------- | -------- | ------ |
| Single large Apex interface with 10+ methods, most implementations leave several empty | High | `{}` or `return null` stubs in implementations |
| Service class interface combines query and command operations (CQRS violation) | Medium | Both `getRecords()` and `updateRecords()` style methods |
| LWC parent `@api` method surface that child components must implement in full, even when only a subset is used | Medium | `@api` methods left empty in children |

Tag finding: `[ISP]`

Source: Apex Developer Guide — Interfaces · Interface Segregation Principle

---

## SOLID — Dependency Inversion Principle (DIP)

| Violation | Severity | Signal |
| --------- | -------- | ------ |
| `new ConcreteClass()` instantiation inside a high-level service or handler (no injection, no factory) | High | `AccountSelector sel = new AccountSelector()` hard-wired |
| No mock-friendly abstraction — tests must insert real records because code cannot accept a mock | High | `@SeeAllData=true` or large record inserts |
| Apex class directly calls `System.HTTP`, `Database.insert` without a wrapper for testing | Medium | No `HttpCalloutMock`, no injectable service interface |
| Flow calls a hard-wired Invocable Apex class with no routing via Custom Metadata | Medium | Single Invocable Action hard-coded |
| LWC imports wire adapter directly without mock file for Jest | Low | No `@salesforce/apex` mock setup |

Tag finding: `[DIP]`

Source: Salesforce Developer Blog — Dependency Injection in Apex · LWC Developer Guide — Unit Testing with Jest

---

## Cross-cutting SOLID signals

| Signal | Principle(s) | Severity |
| ------ | ------------ | -------- |
| Class with >300 lines and no clear single purpose | SRP | High |
| No interfaces or abstract classes in any service or handler layer | OCP, DIP | Medium |
| Interface with empty method stubs in multiple implementations | ISP, LSP | Medium |
| Hard-wired concrete dependencies that make unit testing require real data | DIP | High |
| Over-abstraction: interface with exactly one implementation, no extension planned | OCP, OE | Medium (Over-Engineering) |

---

## Positive patterns to confirm

When present, note these as correctly implemented:

- Trigger delegates immediately to a handler class with no business logic in the trigger body
- SOQL results collected into `Map<Id, SObject>` before loop processing
- `Database.insert(records, false)` with explicit `SaveResult` error handling
- Custom Metadata or Custom Settings used for all configurable values
- LWC properties are reactive with no direct DOM mutation
- Flow uses collection variables and single DML elements outside loops
- Trigger delegates to a metadata-driven dispatcher with no hardcoded branch per record type (OCP)
- Service class accepts a Selector interface via constructor injection (DIP)
- Apex interfaces are narrow and cohesive — one interface per responsibility (ISP)
- Abstract base class defines a stable contract; subclasses only extend without contradicting post-conditions (LSP)
- Each handler class addresses a single business concern under 200 lines (SRP)
