---
name: sf-deployment
description: "Use when reviewing Salesforce deployment artifacts: package.xml, destructiveChanges.xml, scratch org definition, .forceignore, CI/CD pipeline configs, pre/post deployment scripts. Trigger phrases: deployment review, package.xml, destructiveChanges, scratch org, .forceignore, CI/CD, pipeline, sfdx, devops, release."
---

Only assess what is visible in the provided artifacts. State "Unable to assess — no deployment artifacts provided" if none are present.

## package.xml completeness

| Check                                                                                                         | Severity if violated |
| ------------------------------------------------------------------------------------------------------------- | -------------------- |
| A custom field is included but its parent object metadata type is omitted                                     | High                 |
| A Flow is included but referenced Custom Object or Custom Field is omitted                                    | High                 |
| A Permission Set is included but the Object Settings or Field Permissions it grants are not deployed together | High                 |
| A Lightning Web Component is included but its associated StaticResource is omitted                            | Medium               |
| Metadata types included that require Feature Licenses not confirmed in target org                             | Medium               |

Source: Salesforce Metadata API Developer Guide — package.xml Samples

## destructiveChanges.xml risks

| Check                                                                            | Severity if violated |
| -------------------------------------------------------------------------------- | -------------------- |
| Object targeted for deletion has active Master-Detail children in scope          | Critical             |
| Custom field targeted for deletion has active Formula field references           | High                 |
| Custom field targeted for deletion has active Flow or Process Builder references | High                 |
| Picklist value deletion without confirming no records hold that value            | High                 |
| Apex class deletion without confirming no active schedule job references it      | High                 |

Source: Salesforce Metadata API Developer Guide — Deleting Components from an Organization

## Scratch org definition

| Check                                                                               | Severity if violated |
| ----------------------------------------------------------------------------------- | -------------------- |
| `ServiceCloud` feature missing but Service Cloud objects/components are present     | High                 |
| `ContactsToMultipleAccounts` missing but multi-account relationship used            | High                 |
| `Communities` or `ExperienceBundle` missing but Experience Cloud components present | High                 |
| `Translation` missing but translation metadata included                             | Medium               |
| `MultiCurrency` missing but currency fields or multi-currency logic present         | High                 |
| `orgPreferences` does not enable features used by detected components               | Medium               |

Source: Salesforce DX Developer Guide — Scratch Org Definition File

## .forceignore

| Check                                             | Severity if violated |
| ------------------------------------------------- | -------------------- |
| `.forceignore` file absent entirely               | Medium               |
| `.sfdx/` not excluded                             | Medium               |
| `lwc/**/__mocks__` not excluded                   | Medium               |
| `node_modules/` not excluded                      | Medium               |
| `.DS_Store` or OS-specific artifacts not excluded | Low                  |

Source: Salesforce DX Developer Guide — .forceignore

## CI/CD pipeline

| Check                                                                             | Severity if violated |
| --------------------------------------------------------------------------------- | -------------------- |
| No pre-deployment validation step (e.g. `sf project deploy validate`)             | High                 |
| No post-deployment script for permission set assignments or data seeding          | Medium               |
| Apex test run omitted from deployment step                                        | Critical             |
| Secrets or credentials visible in pipeline config (not sourced from secret store) | Critical             |
| No rollback or destructive post-deploy recovery mechanism documented              | Medium               |
| Deployment targets production directly without sandbox validation step            | High                 |

Source: Salesforce DX Developer Guide
