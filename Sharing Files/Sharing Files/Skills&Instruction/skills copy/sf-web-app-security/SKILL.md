---
name: sf-web-app-security
description: "Use when reviewing Salesforce web-layer security controls: static resource exposure, CSRF prevention, open redirect, file upload validation, clickjack and CSP protection. Trigger phrases: static resource security, CSRF, open redirect, file upload, clickjack, content security policy, CSP header, X-Frame-Options, PageReference redirect, GET state change."
---

Review against the Salesforce Security Implementation Guide and OWASP Top 10. Only flag what is observable in the input. Do not fetch any external URLs.

---

## Static resource security (ruleset ID 5)

| Check | Severity |
| ----- | -------- |
| Static resource `cacheControl` set to `Public` and the resource contains sensitive or proprietary data | High |
| Static resource metadata absent — `cacheControl` cannot be verified | Medium |
| Sensitive configuration values (API keys, tokens, URLs) embedded in static resource JS or CSS | Critical |
| Static resources referenced via a hardcoded path string instead of the `$Resource` global variable in LWC or Visualforce | High |
| Static resource could be accessed by unauthenticated users and no CSP restriction limits its loading origin | Medium |

Source: Salesforce Help — Static Resources · Salesforce Security Implementation Guide

---

## CSRF prevention (ruleset ID 8)

| Check | Severity |
| ----- | -------- |
| Visualforce controller method performing DML or state change is invokable via HTTP GET (no `@ReadOnly` or POST-only enforcement) | High |
| Custom Apex REST endpoint annotated `@HttpGet` performs DML or a state-changing operation | Critical |
| `@RemoteAction` method performs DML and does not rely on Salesforce's built-in CSRF token protection | High |
| `apex:form` bypassed in favor of a raw `<form>` element without Salesforce CSRF token inclusion | High |
| `@AuraEnabled` method performs DML and is accessible without session context enforcement | Medium |

Source: Salesforce Security Implementation Guide — CSRF · Apex Developer Guide — Apex REST Annotations

---

## Open redirect prevention (ruleset ID 12)

| Check | Severity |
| ----- | -------- |
| `PageReference` constructed directly from a raw user-input value without whitelist validation | Critical |
| `ApexPages.currentPage().getParameters().get(...)` result used directly as a redirect target | Critical |
| `retURL`, `startURL`, or equivalent query parameter accepted and passed to `PageReference` without validation | High |
| `NavigationMixin.Navigate` target URL in LWC built from a user-supplied string without sanitization | High |
| Redirect destination not validated against a documented whitelist of trusted domains | High |

Source: Salesforce Security Implementation Guide — Open Redirect Prevention · OWASP Top 10 — A01

---

## File upload security (ruleset ID 13)

| Check | Severity |
| ----- | -------- |
| Apex inserting `ContentVersion` or `Attachment` records without validating `FileExtension` or MIME type against an allowlist | High |
| No maximum file size check before insert — relies solely on org-level file size limits | Medium |
| Dangerous file extensions (`.exe`, `.js`, `.html`, `.sh`, `.bat`, `.php`) not explicitly blocked in upload handler | Critical |
| No virus/content scanning integration (e.g. external DLP service) referenced for uploaded files | Medium |
| Uploaded file retrieved and served back to end users without `Content-Disposition` or content-type enforcement | High |
| `ContentVersion.VersionData` written to a page response or download link without attachment-forcing headers | High |

Source: Salesforce Security Implementation Guide — File Upload Security · OWASP Top 10 — A05

---

## Clickjack and CSP protection (ruleset ID 14)

| Check | Severity |
| ----- | -------- |
| Visualforce page rendered with `showHeader="false"` or inside an iframe context without `X-FRAME-OPTIONS: SAMEORIGIN` or `DENY` confirmed in org settings | High |
| Custom LWC or Aura component loads a script from an external domain not listed in org CSP Trusted Sites | High |
| Inline `<script>` block or `eval()` present in a context where CSP `strict-dynamic` would block it | High |
| No CSP Trusted Sites entry documented for third-party analytics, fonts, or libraries loaded by LWC | Medium |
| Experience Cloud site frame-src CSP directive does not restrict framing to trusted domains only | High |

Source: Salesforce Security Implementation Guide — Clickjack Protection · Salesforce Help — Content Security Policy Overview
