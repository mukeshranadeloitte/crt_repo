---
name: sf-package-review
description: "Use when reviewing Salesforce unlocked packages, managed packages (1GP/2GP), or ISV distribution configurations: namespace collision, API version pinning, subscriber impact of destructive changes, permission set distribution, and package dependency management. Trigger phrases: unlocked package review, managed package review, namespace, 1GP review, 2GP review, ISV packaging, package dependencies, packageDirectories, packageAliases, package version."
---

Review against the Salesforce DX Developer Guide, ISV Technical Success documentation, and AppExchange Security Review guidelines. Only flag what is observable in the input — sfdx-project.json, package version metadata, permission set XML, or design documents. Do not fetch any external URLs.

---

## Package structure and sfdx-project.json

| Check | Severity |
| ----- | -------- |
| `sfdx-project.json` has no `namespace` defined for a managed (1GP/2GP) package | Critical |
| `packageDirectories` contains a mix of packaged and unpackaged metadata without clear `default` designation | High |
| `packageAliases` entries reference package versions that do not exist in the org's Dev Hub — stale alias risk | High |
| Package dependency declared in `packageAliases` without a pinned version ID — floating dependency creates non-deterministic installs | High |
| `ancestorId` absent on a 2GP managed package that has breaking changes — prevents enforcing upgrade path | High |
| No `definitionFile` reference to a scratch org definition in `sfdx-project.json` — reproducible dev environment not guaranteed | Medium |

Source: Salesforce DX Developer Guide — Project Configuration File

---

## API version pinning

| Check | Severity |
| ----- | -------- |
| Packaged Apex class or metadata component has an `apiVersion` that differs from the package's target API version | Medium |
| Package target API version is below the minimum supported version for subscriber org releases in scope | High |
| Packaged Flow API version is below 55.0 — pre-Flow Builder tooling support limited for subscribers | High |
| Package version is tested only against the build org API version — subscriber orgs on newer API versions may behave differently | Medium |

Source: Salesforce Metadata API — API Versioning Guidelines · Salesforce DX Developer Guide — Package Version

---

## Subscriber impact of destructive changes

| Check | Severity |
| ----- | -------- |
| Package version removes a `global` Apex class, method, or variable — breaking change for subscribers who reference it | Critical |
| Package version removes a `global` Apex interface — all subscriber implementations will fail to compile | Critical |
| Package version renames a `global` method signature — non-backward-compatible and blocks upgrade | Critical |
| Custom object or field removed in a new package version without a documented migration path for subscriber data | High |
| Picklist values removed from a packaged global picklist — subscriber records holding those values become orphaned | High |
| Package version deprecates but does not remove a `global` symbol — no deprecation notice in release notes | Medium |

Source: Salesforce ISV Technical Success — Backward Compatibility Requirements · Salesforce DX Developer Guide — Breaking Changes

---

## Permission set and license distribution

| Check | Severity |
| ----- | -------- |
| Packaged permission set grants permissions broader than the minimum required for the package feature | High |
| No packaged permission set provided — subscribers must manually configure permissions on install | Medium |
| Permission set grants `ModifyAllData` or `ViewAllData` — should never be included in a distributable package | Critical |
| Package license type (Salesforce, Platform, Customer Community, etc.) does not match the documented target audience | High |
| `licenseDefinitionKey` absent in the package when a managed package requires Feature License enforcement | Medium |

Source: Salesforce ISV Technical Success — Permission Sets in Packages · AppExchange Security Review Checklist

---

## Namespace and collision risk

| Check | Severity |
| ----- | -------- |
| Custom object or field API name in an unlocked package uses a generic name (e.g. `Status__c`, `Type__c`) without namespace — high collision risk in subscriber orgs | High |
| Namespace prefix absent on a managed package metadata component despite namespace being registered | Critical |
| Apex class name in an unlocked package shares a name with a well-known open-source library or AppExchange package | Medium |
| Static resource name in an unlocked package is not namespaced — risk of overwriting subscriber's existing static resource | High |

Source: Salesforce DX Developer Guide — Namespaces · AppExchange Security Review

---

## Package CI/CD and version promotion

| Check | Severity |
| ----- | -------- |
| No automated package version creation step in CI/CD pipeline — version created manually with no audit trail | High |
| Package version not validated against a subscriber-representative scratch org before promotion to Beta | High |
| No automated AppExchange Security Review pre-check (e.g. `sf scanner run` against package source) before upload | Medium |
| Package version promoted to Released without Apex test run achieving 75%+ coverage in a full scratch org | Critical |
| No rollback strategy documented for a subscriber org that fails upgrade — subscribers remain on broken version | High |

Source: Salesforce DX Developer Guide — Package Development Model · AppExchange Security Review
