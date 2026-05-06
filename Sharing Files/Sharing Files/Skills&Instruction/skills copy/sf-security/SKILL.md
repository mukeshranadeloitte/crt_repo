---
name: sf-security
description: "Use when reviewing Salesforce security: sharing model, CRUD/FLS, SOQL injection, hardcoded IDs/credentials, LWC Locker Service, platform security, guest user access, permission sets, compliance markers. Trigger phrases: security review, sharing model, FLS, SOQL injection, permission set, guest user, hardcoded, credentials."
---

Only flag what is present in the input. Every finding must cite a Salesforce source.

## Apex security

| Check                                                                                                       | Severity if violated |
| ----------------------------------------------------------------------------------------------------------- | -------------------- |
| Class declares `with sharing`, `without sharing`, or `inherited sharing`                                    | High (absence)       |
| Dynamic SOQL uses `String.escapeSingleQuotes` or bind variables — no raw string concatenation of user input | Critical             |
| SOQL/DML preceded by `Schema.sObjectType` describe check or `Security.stripInaccessible`                    | High                 |
| No hardcoded record IDs, org IDs, profile IDs, or permission set IDs                                        | Critical             |
| No hardcoded API keys, tokens, passwords, or named credential values                                        | Critical             |
| Manual share record creation includes a documented sharing reason                                           | Medium               |
| Callouts: timeout set, endpoint from Named Credential (not hardcoded), response validated                   | High                 |

Source: Apex Developer Guide — Apex Security and Sharing

## LWC / Aura security

| Check                                                                        | Severity if violated |
| ---------------------------------------------------------------------------- | -------------------- |
| No direct DOM access across component boundaries (Locker Service compliance) | High                 |
| Wire adapters use only supported, documented APIs                            | Medium               |
| `@AuraEnabled(cacheable=true)` only on read-only methods that enforce FLS    | High                 |
| No `innerHTML` assignment or `eval` with dynamic/user-supplied content       | Critical             |

Source: Salesforce LWC Security Guide

## Platform security

| Check                                                                                 | Severity if violated |
| ------------------------------------------------------------------------------------- | -------------------- |
| Guest user profile does not have access to sensitive object/field permissions         | High                 |
| Connected app: IP restrictions set, token expiry configured, OAuth scopes minimal     | High                 |
| Sensitive object permissions granted via Permission Set Groups, not profiles directly | Medium               |
| Sensitive operations require High Assurance session security level                    | High                 |

Source: Salesforce Security Implementation Guide

## Compliance markers (flag if detectable)

- PII fields (SSN, email, phone, DOB) with no Shield Field Encryption or field history tracking noted in design — flag as High.
- Custom objects storing sensitive data with no `CreatedById` / `LastModifiedById` equivalent audit trail — flag as Medium.
- Regulated-data objects (HIPAA, PCI, GDPR scope) without sharing rule documentation — flag as High.

Source: Salesforce Shield — Platform Encryption Overview

## Named Credentials and External Credentials

| Check | Severity if violated |
| ----- | -------------------- |
| HTTP callout endpoint hardcoded as a URL string instead of a Named Credential reference | High |
| Legacy Named Credential type used where External Credential + Principal pattern is available (API v53.0+) | Medium |
| External Credential principal configured with `Managed` authentication type but no permission set grants documented for it | High |
| OAuth Named Credential scope broader than the minimum required for the integration | High |
| Named Credential or External Credential accessible to profiles or permission sets beyond the minimum required population | Medium |
| Apex callout uses `HttpRequest.setHeader('Authorization', ...)` to manually set auth instead of Named Credential merge field | High |

Source: Salesforce Help — Named Credentials · Salesforce Help — External Credentials

## Cannot assess without org configuration

The following areas cannot be verified from code or design documents alone. State "Unable to assess — org configuration required" for each:

- Actual sharing rule definitions (OWD, criteria-based, owner-based)
- Permission set assignments to users
- Guest user profile field-level security settings unless profile XML is provided
- Connected app consumer key / secret rotation status

## Positive patterns to confirm

When present, note these as correctly implemented:

- All HTTP callouts reference Named Credentials — no hardcoded endpoint URLs
- SOQL preceded by `Security.stripInaccessible` with appropriate access type
- All Apex classes explicitly declare a sharing keyword
- LWC components use only supported, documented wire adapters
- PII fields documented as encrypted via Shield or flagged for encryption planning
