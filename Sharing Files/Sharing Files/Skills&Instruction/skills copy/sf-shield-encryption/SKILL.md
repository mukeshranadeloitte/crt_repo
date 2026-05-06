---
name: sf-shield-encryption
description: "Use when reviewing Salesforce Shield Platform Encryption configuration: encryption key rotation, tenant secret management, Manage Encryption Keys permission, current key enforcement, PII field encryption coverage. Trigger phrases: Shield encryption, Platform Encryption, tenant secret, encryption key, key rotation, Manage Encryption Keys, View Encrypted Data, encrypted fields, PII encryption, HIPAA encryption."
---

Review against the Salesforce Shield Platform Encryption documentation, NIST SP 800-57, and MARS-E 2.0 / HIPAA requirements. Only flag what is observable in the input — permission set XML, profile metadata, Apex referencing encrypted fields, or design documents. Do not fetch any external URLs.

---

## Encryption key rotation (ruleset ID 18)

| Check | Severity |
| ----- | -------- |
| Design document or encryption policy does not specify a key rotation schedule | High |
| Documented key rotation frequency exceeds 12 months with no risk-based justification | High |
| No emergency key rotation procedure documented for suspected compromise scenarios | Critical |
| Apex code reads encrypted field values and writes them to `System.debug`, a log object, or an outbound payload without masking | Critical |
| No process defined to notify data owners when a key rotation has been completed | Medium |

Source: Salesforce Shield Platform Encryption — Tenant Secrets and Key Management · MARS-E 2.0 — SC-12

---

## Encryption key storage outside Salesforce (ruleset ID 19)

| Check | Severity |
| ----- | -------- |
| Design document does not specify exporting and storing the tenant secret backup outside the Salesforce org | High |
| No named owner or designated team documented for safeguarding the exported tenant secret | High |
| Tenant secret backup access is not restricted to a documented set of privileged users | High |
| Key backup stored in a location accessible to the same user population as the Salesforce org itself (no separation of duties) | High |

Source: Salesforce Shield Platform Encryption — Export Your Tenant Secret · NIST SP 800-57 Part 1 — Key Management

---

## Manage Encryption Keys and View Encrypted Data permissions (ruleset ID 20)

These checks apply when permission set or profile metadata XML is provided.

| Check | Severity |
| ----- | -------- |
| `ManageEncryptionKeys` system permission granted to a permission set with broad or non-privileged user assignment | Critical |
| `ViewEncryptedData` system permission granted without documented business justification in design | High |
| Permission set containing `ManageEncryptionKeys` has no IP range restriction or High Assurance session level requirement | High |
| `ManageEncryptionKeys` granted via a Profile rather than a dedicated restricted Permission Set — violates separation of duties | Medium |
| No periodic access review process documented for users holding `ManageEncryptionKeys` | High |

Source: Salesforce Shield Platform Encryption — Assign Encryption Permissions · Salesforce Security Implementation Guide — Least Privilege

---

## Current key enforcement (ruleset ID 21)

| Check | Severity |
| ----- | -------- |
| Design document does not describe a re-encryption process after key rotation (Data Sync or Shield background re-encryption job) | High |
| Apex batch or bulk job reads encrypted fields without a documented check that records are encrypted under the current key generation | Medium |
| No process documented to verify all regulated-data records are encrypted under the most recent key | High |
| Key rotation performed but no validation step confirms previously encrypted records have been migrated to the new key | High |

Source: Salesforce Shield Platform Encryption — Rotate Your Encryption Key · MARS-E 2.0 — SC-28
