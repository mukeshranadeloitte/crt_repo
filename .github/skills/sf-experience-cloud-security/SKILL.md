---
name: sf-experience-cloud-security
description: "Use when reviewing Salesforce Experience Cloud (Community) security: guest user permissions, network member object security, unauthenticated Apex exposure, CSP for community pages, Aura app security, and Experience Cloud site configuration risks. Trigger phrases: experience cloud security, guest user security, community security, network member security, guest user permissions, community site security, digital experience security."
---

Review against the Salesforce Experience Cloud Security Guide, Salesforce Security Implementation Guide, and OWASP Top 10. Only flag what is observable in the input — Guest User profile XML, Network metadata, Apex classes exposed to guest context, or design documents. Do not fetch any external URLs.

---

## Guest User profile and permissions

| Check | Severity |
| ----- | -------- |
| Guest User profile grants Create, Edit, or Delete permissions on any custom or standard object | Critical |
| Guest User profile grants Read access to objects containing PII, financial, or regulated data without documented justification | High |
| Guest User profile has access to fields not required for the unauthenticated use case — field-level security not minimised | High |
| Object-level sharing not set to Private for sensitive objects accessible from the community — relies solely on profile to restrict guest access | High |
| Guest User profile grants access to Apex classes that perform DML or return sensitive data without explicit sharing and FLS enforcement | Critical |

Source: Salesforce Help — Control Access with the Guest User Profile · Salesforce Security Implementation Guide

---

## Unauthenticated Apex exposure

| Check | Severity |
| ----- | -------- |
| Apex class invoked from a guest Experience Cloud page does not declare `with sharing` | Critical |
| `@AuraEnabled` method accessible without session validation returns records beyond the guest user's sharing access | Critical |
| Wire adapter or Apex controller returns full SObject with all fields — no field projection to limit guest-visible data | High |
| Apex invocable action callable from a guest Screen Flow does not enforce FLS via `Security.stripInaccessible` | High |
| REST endpoint (`@RestResource`) does not check `UserInfo.getUserType() == 'Guest'` before returning regulated data | High |

Source: Salesforce Help — Apex and SOQL in Experience Cloud · Apex Developer Guide — Apex Security and Sharing

---

## Network member and site configuration

| Check | Severity |
| ----- | -------- |
| Experience Cloud site has no login page configured but contains pages with record creation or data submission | High |
| Self-registration enabled with no email verification step — allows arbitrary account creation | High |
| Account record used as community member account is shared with Guest User sharing rules allowing broader access | High |
| Content Snap-in or embedded Chat configured without authentication enforcement on sensitive pages | Medium |
| Site-level sharing settings do not restrict sharing rules applied to the Guest User — effective sharing wider than designed | High |

Source: Salesforce Help — Experience Cloud Security · Salesforce Help — Configure Self-Registration

---

## CSP and clickjack protection for community pages

| Check | Severity |
| ----- | -------- |
| Experience Cloud site frame-src CSP directive does not restrict framing to trusted domains only | High |
| Third-party analytics, fonts, or libraries loaded by community pages are not listed in CSP Trusted Sites for the Experience Cloud site | High |
| Aura app used as the community template without verified Locker Service compliance across all custom components | High |
| Experience Builder page embeds an external iframe without explicit frame-src allowlisting | High |
| No `X-Frame-Options` or equivalent CSP `frame-ancestors` directive configured for the site to prevent clickjacking | High |

Source: Salesforce Security Implementation Guide — Clickjack Protection · Salesforce Help — Content Security Policy for Experience Cloud

---

## Cannot assess without org configuration

The following cannot be verified from code or design documents alone. State "Unable to assess — org configuration required":

- Actual Guest User profile settings in Setup (only verifiable from exported profile XML)
- Network member sharing group composition
- Site-level CSP Trusted Sites configuration
- Self-registration and login flow enablement status
