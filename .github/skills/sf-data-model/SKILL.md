---
name: sf-data-model
description: "Use when reviewing Salesforce data model: object relationships, field design, naming conventions, external IDs, record types, data model violations. Trigger phrases: data model review, object design, relationship design, lookup, master-detail, field naming, external ID, record type, junction object."
---

Only flag what is present in the input. Every finding must cite a Salesforce source.

## Relationship design

| Check                                                                                                                 | Severity if violated |
| --------------------------------------------------------------------------------------------------------------------- | -------------------- |
| Child record has no meaning outside the parent but uses Lookup (should be Master-Detail for cascade delete + roll-up) | Medium               |
| Many-to-many modelled via two lookups and join attributes are present — missing junction object                       | High                 |
| Self-referential lookup with no documented hierarchy purpose                                                          | Medium               |
| Polymorphic lookup (What/Who) used on a custom object — unsupported                                                   | High                 |
| Lookup relationship on child object where orphan records would be invalid data                                        | Medium               |

Source: Salesforce Object Reference — Relationships Among Objects

## Field design

| Check                                                                                      | Severity if violated         |
| ------------------------------------------------------------------------------------------ | ---------------------------- |
| Text field stores comma-separated IDs, JSON blobs, or pipe-delimited values                | High                         |
| Formula field references 5+ levels of relationship traversal                               | Medium (governor limit risk) |
| Roll-up summary attempted on a Lookup relationship via trigger workaround                  | Medium                       |
| Currency field with no multi-currency consideration noted                                  | Medium                       |
| Number field used as a boolean flag (0/1) instead of Checkbox                              | Low                          |
| Number field used as a status indicator instead of Picklist                                | Low                          |
| High-volume object (expected >100K records) has no indexed field in SOQL WHERE clauses     | High                         |
| Long Text Area or Rich Text Area used where a structured child object would be appropriate | Medium                       |

## Object design

| Check                                                                                                      | Severity if violated |
| ---------------------------------------------------------------------------------------------------------- | -------------------- |
| Custom object replicates a standard Salesforce object (custom Contact, custom Opportunity, etc.)           | High                 |
| External ID field absent on objects that are targets of integration upserts                                | High                 |
| Record types used solely for minor field visibility differences (page layouts or dynamic forms sufficient) | Low                  |
| Required fields absent on objects created programmatically — missing validation at entry point             | High                 |
| Custom object used for configuration data that belongs in Custom Metadata Types or Custom Settings         | Medium               |

## Naming and conventions

| Check                                                                          | Severity if violated           |
| ------------------------------------------------------------------------------ | ------------------------------ |
| Object API name does not follow `PascalCase` convention                        | Low                            |
| Field API name does not follow `snake_case` convention                         | Low                            |
| Label and API name diverge significantly (causes confusion in schema describe) | Low                            |
| `__c` field on a managed package object modified via trigger                   | High (packaging conflict risk) |
| Field labels that expose internal system terminology to end users              | Low                            |

Source: Salesforce Architect — Data Modeling Overview · Salesforce Object Reference
