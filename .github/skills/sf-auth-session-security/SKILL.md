---
name: sf-auth-session-security
description: "Use when reviewing Salesforce authentication and session security controls: password policies, MFA enforcement, SSO configuration, session timeout, session IP locking, account lockout, session token security. Trigger phrases: password policy, MFA, multi-factor authentication, SSO, session timeout, session lockout, account lockout, session IP, session token, CAPTCHA, account verification, re-authentication."
---

Review against the Salesforce Security Implementation Guide, Salesforce Identity and Access Management guide, and MARS-E 2.0 requirements. Only flag what is observable in the input — connected app metadata, profile or permission set XML, design documents, or Apex that handles authentication or session logic. Do not fetch any external URLs.

---

## Password policy

These checks apply when profile metadata, session settings documentation, or design documents are provided.

| Check | Severity |
| ----- | -------- |
| Design document or profile metadata specifies a minimum password length below 8 characters | High |
| No password complexity requirement documented (uppercase, lowercase, number, special character combination) | High |
| No password expiration policy documented — recommended cadence is 90–180 days | High |
| No password history policy documented — minimum: last 5 passwords must not be reused | Medium |
| Apex or integration code transmits a password or credential to a third-party system in clear text (not via Named Credential or encrypted channel) | Critical |

Source: Salesforce Security Implementation Guide — Password Policies · MARS-E 2.0 — IA-5

---

## MFA and SSO enforcement

These checks apply when connected app metadata, identity provider configuration, or design documents are provided.

| Check | Severity |
| ----- | -------- |
| Connected app metadata sets `permittedUsers` to `AllUsers` without MFA enforcement noted in design | High |
| Connected app `oauthConfig` grants OAuth scopes broader than the minimum required for the integration | High |
| Connected app has no IP range restriction defined and no MFA compensating control documented | Medium |
| Design document describes access to sensitive or regulated data without specifying MFA re-authentication at the point of access | High |
| No CAPTCHA or re-authentication step documented for data export or bulk download workflows | Medium |
| Sensitive connected app (e.g. backup tool, reporting tool, integration middleware) has no SSO/IdP integration documented | Medium |

Source: Salesforce Security Implementation Guide — MFA Implementation Guide · Salesforce Identity — Connected App OAuth Policies

---

## Account verification link expiry

| Check | Severity |
| ----- | -------- |
| Design document or session settings specification allows account verification link validity exceeding 3 days | Medium |
| No expiry duration specified for account verification links sent in new user welcome emails | Medium |

Source: Salesforce Security Implementation Guide — Login and Verification Settings · Salesforce Help — Session Settings

---

## Session IP locking

| Check | Severity |
| ----- | -------- |
| Design document or session settings specification does not require sessions to be locked to the originating IP address | High |
| Apex code or integration stores a session token in a way that does not enforce IP-origin binding (e.g. token passed across network without IP check) | High |

Source: Salesforce Security Implementation Guide — Session Settings · MARS-E 2.0 — AC-17

---

## Session timeout and account lockout

| Check | Severity |
| ----- | -------- |
| Design document or session settings specification allows session inactivity timeout exceeding 30 minutes | High |
| No session inactivity timeout documented at all | High |
| Account lockout threshold specified as more than 5 incorrect login attempts | Medium |
| No account lockout policy documented | High |

Source: Salesforce Security Implementation Guide — Session Settings · MARS-E 2.0 — AC-7

---

## Session token security

These checks apply when Visualforce pages, Apex controllers, LWC, or any session-handling code is present.

| Check | Severity |
| ----- | -------- |
| Session token stored in a client-side accessible location such as `localStorage` or `sessionStorage` in LWC JavaScript | Critical |
| Session token passed as a URL query parameter in a Visualforce page URL or custom redirect | High |
| Visualforce page with `contentType` override does not configure `Cache-Control` to exclude session cookies from caching | High |
| Session token not invalidated on logout in custom session management Apex code | Critical |
| Custom authentication flow does not rotate the session token after successful login — session fixation risk | High |

Source: Salesforce Security Implementation Guide — Session Management · OWASP Top 10 — A07 · MARS-E 2.0 — SC-23
