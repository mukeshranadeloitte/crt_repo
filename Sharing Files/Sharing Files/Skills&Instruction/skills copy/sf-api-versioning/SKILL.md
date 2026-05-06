---
name: sf-api-versioning
description: "Use when reviewing Salesforce API versions in metadata files, deprecated APIs, LWC js-meta.xml apiVersion, Flow API version, Apex API version, obsolete Aura components, deprecated platform features. Trigger phrases: API version, apiVersion, deprecated API, metadata version, LWC version, Flow version, Aura deprecation, obsolete API."
---

Only flag what is present in the input. Every finding must cite a Salesforce source.

## Metadata API version

| Check                                                               | Severity if violated                                                |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Any metadata file declares `apiVersion` below 55.0 (Winter '22)     | Medium — flag and recommend updating to current release API version |
| Any metadata file declares `apiVersion` below 45.0 (Spring '19)     | High — risk of deprecated behaviour no longer supported             |
| `apiVersion` absent from a metadata XML file entirely               | Medium                                                              |
| Mixed API versions across components in the same deployment package | Medium — can cause inconsistent behaviour                           |

Current stable API version: 63.0 (Spring '25). Flag anything below 58.0 as requiring upgrade planning. Verify the exact current version from the org's Setup > Apex Classes page or the Metadata API release notes if a newer release has shipped.

Source: Salesforce Metadata API — API Versioning Guidelines

## LWC js-meta.xml

| Check                                                                                                                                     | Severity if violated |
| ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| `<apiVersion>` below the org minimum supported LWC API version                                                                            | High                 |
| `<apiVersion>` not present in `js-meta.xml`                                                                                               | Medium               |
| `targets` configuration exposes the component to contexts it is not designed for (e.g. `lightning__AppPage` with no property definitions) | Low                  |

Source: Salesforce LWC Component Configuration File Reference

## Flow API version

| Check                                                                          | Severity if violated                                    |
| ------------------------------------------------------------------------------ | ------------------------------------------------------- |
| Flow `processMetadataValues` or `apiVersion` below 50.0 (Winter '21)           | High — pre-Flow Builder format, tooling support limited |
| Flow `apiVersion` below 55.0                                                   | Medium                                                  |
| Process Builder (`processType = Workflow`) active — flag for migration to Flow | High (deprecated platform feature)                      |
| Workflow Rules active — flag for migration to Flow                             | High (retired in new orgs, maintenance-only mode)       |

Source: Salesforce Metadata API — Flow Metadata · Workflow Rules Retirement FAQ

## Deprecated platform features

| Check                                                                                        | Severity if violated                |
| -------------------------------------------------------------------------------------------- | ----------------------------------- |
| Aura component used where an equivalent LWC exists or can be built                           | Medium — flag for migration roadmap |
| `lightning:container` used in Aura — deprecated; use LWC `lightning-container`               | High                                |
| `sforce.one` JavaScript API calls in Aura or LWC — deprecated                                | High                                |
| `$A.createComponent` used at runtime — avoid; use conditional rendering                      | Medium                              |
| Visualforce page used for data entry where a Lightning Flow or LWC Screen Flow would suffice | Medium                              |
| `platform:actionableItem` interface in Aura — removed in API v57.0+                          | High                                |
| `ConnectApi` methods deprecated in the current API version and still in use                  | High                                |

Source: Salesforce LWC — Migrate Aura to LWC · Apex Deprecated Features

## Apex class API version

| Check                                                                             | Severity if violated                                                                  |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Apex class saved at API version below 50.0                                        | Medium — behavioural differences in sharing, SOQL nulls, and list iteration may apply |
| Apex class API version does not match the API version of Flows it is invoked from | Low — version boundary behaviour risk                                                 |

Source: Apex Developer Guide — Governor Limits per API Version
