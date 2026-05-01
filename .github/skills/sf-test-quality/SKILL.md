---
name: sf-test-quality
description: "Use when reviewing Salesforce Apex test classes for quality, coverage, assertions, bulk testing, negative tests, mock callouts, SeeAllData usage, TestSetup. Trigger phrases: test quality, test coverage, unit test, assert, mock callout, SeeAllData, bulk test, negative test, TestSetup."
---

Review test classes against these standards. Every finding must cite a Salesforce source.

## Coverage standards

| Check                                                                        | Severity if violated      |
| ---------------------------------------------------------------------------- | ------------------------- |
| Class or trigger has 0% coverage                                             | Critical                  |
| Class or trigger has coverage below 75% (platform deployment floor)          | High                      |
| Coverage achieved by assertion-free tests (line execution only)              | High                      |
| `System.assert(true)` present                                                | Critical — false coverage |
| `System.assertNotEquals(null, null)` or equivalent no-op assertion           | Critical — false coverage |
| Test uses `System.assertEquals` without meaningful expected vs actual values | Medium                    |

Source: Apex Testing Best Practices (Apex Developer Guide)

## Test structure

| Check                                                                                                                        | Severity if violated |
| ---------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| `@SeeAllData=true` without documented justification (e.g. standard price book)                                               | High                 |
| Test method does not call `Test.startTest()` / `Test.stopTest()` where governor-limit isolation or async execution is needed | Medium               |
| No `@TestSetup` method when the same data setup is repeated across multiple test methods                                     | Low                  |
| Test method name does not describe the scenario being tested                                                                 | Low                  |

## Bulk testing

| Check                                                             | Severity if violated |
| ----------------------------------------------------------------- | -------------------- |
| Trigger has no test passing ≥ 200 records                         | High                 |
| Batch class has no test passing ≥ 200 records                     | High                 |
| Test uses `insert record` (single record) for bulk-sensitive code | Medium               |

## Negative and boundary tests

| Check                                                             | Severity if violated |
| ----------------------------------------------------------------- | -------------------- |
| No test covers invalid input or missing required field            | Medium               |
| No test covers permission denial (running as user without access) | Medium               |
| No test covers exception / error handling paths                   | Medium               |
| No test covers empty collection inputs to bulk methods            | Low                  |

## Callout and integration mocking

| Check                                                                           | Severity if violated |
| ------------------------------------------------------------------------------- | -------------------- |
| Test makes real HTTP callout — `HttpCalloutMock` not implemented                | Critical             |
| `Test.setMock(HttpCalloutMock.class, ...)` not called before `Test.startTest()` | High                 |
| Mock response does not cover error status codes (4xx, 5xx)                      | Medium               |

## Data isolation

| Check                                                                  | Severity if violated |
| ---------------------------------------------------------------------- | -------------------- |
| Test depends on org data not created within the test or `@TestSetup`   | High                 |
| Test queries or references a record ID hardcoded from a specific org   | Critical             |
| Test relies on a static resource that may not exist in all target orgs | Medium               |

Source: Apex Testing Guide (Apex Developer Guide)

## Integration and end-to-end test coverage

| Check | Severity if violated |
| ----- | -------------------- |
| Integration component (callout, REST endpoint, Platform Event publisher) has no test verifying the full request/response contract via `HttpCalloutMock` | High |
| Multi-object trigger chain has no test verifying end-to-end record state after `Test.stopTest()` | High |
| Batch class followed by a Queueable or Platform Event publish has no test verifying the async hand-off using `Test.stopTest()` | High |
| Inbound REST endpoint tested only with valid input — no test for malformed payload, missing required fields, or auth failure | High |
| Screen Flow or Experience Cloud page has no functional test plan documented for the golden path | Medium |
| External system integration has no contract test or schema validation step documented | Medium |
| Scheduled job has no test verifying it executes under `Test.startTest()/stopTest()` with the correct cron expression format | Medium |

Source: Apex Testing Best Practices — Integration Testing · Salesforce Help — Testing Asynchronous Code
