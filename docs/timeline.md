# Investigation Timeline

## 1. Overview

This document records the chronological progression of the HDFC Android APK investigation.

It covers the major examination phases, artifact discoveries, code-analysis activities, infrastructure observations and documentation milestones.

The timeline is based on available investigation records. Exact timestamps are included only where they were recorded.

**Time standard:** UTC

**Investigation approach:** Static APK Analysis and Passive Infrastructure Intelligence.

**Dynamic analysis:** Not performed.

---

## 2. Investigation Timeline

### Phase 1 — Primary APK Identification

**Date:** Not recorded  
**Activity:** Initial artifact examination

The investigation began with the identification and examination of an Android application labelled **HDFC BANK LOAN SERVICE**.

The primary APK was examined to establish its identity and cryptographic attributes.

Key observations:

- Application package identified as `com.sec.android.app.finance.kaxqj68`.
- Application version identified as `2.9.65`.
- Minimum SDK identified as 24.
- Target SDK identified as 37.
- Signing certificate subject identified as `CN=editor`.
- RSA 2048 signing key identified.
- SHA-256 fingerprint recorded.

<details>
<summary>Primary APK SHA-256</summary>

```text
08cfe1f957d7539320eaaa97f1d6838182f5df57e6f875d00dc3060e432d35af
```

</details>

**Outcome:** Primary APK identity and cryptographic fingerprint documented.

### Phase 2 — APK Structural Examination

**Date:** Not recorded  
**Activity:** Archive and application structure examination

The APK archive was examined to understand its internal composition.

The examination covered:

- Android manifest.
- DEX files.
- Application resources.
- Assets.
- Native libraries.
- Embedded files.

The manifest and application components were examined to identify permissions, services and broadcast receivers relevant to the investigation.

**Outcome:** Application structure and relevant components identified for further analysis.

### Phase 3 — Embedded APK Discovery and Recovery

**Date:** Not recorded  
**Activity:** Embedded artifact examination

An encrypted asset named `rmtley9lr.db` was identified inside the primary APK.

Further examination identified a repeating-XOR transformation used to decode the asset.

The decoded artifact was identified as a secondary Android APK.

| Attribute | Value |
|---|---|
| Original asset | `rmtley9lr.db` |
| Decoded package | `com.nxtwave.support` |
| Version | `1.0` |
| Minimum SDK | 25 |
| Target SDK | 34 |

The recovered APK's SHA-256 was recorded:

```text
13f93b8c70881f9414944fdc55811bfc627dbec966f023c664eb98782690cb4c
```

ZIP integrity verification passed, with 986 archive entries identified.

Unusual absolute-style and backslash-containing archive paths were also documented.

**Outcome:** Secondary APK recovered, identified and examined separately. Its execution relationship with the primary application was not established.

### Phase 4 — SMS Functionality Examination

**Date:** Not recorded  
**Activity:** Java and Smali analysis

The investigation examined SMS-related application components, including:

- `SmsService.java`
- `SmsReceiver.java`
- `SmsForwardService.java`
- `SmsSendService.java`
- `F1/o.java`
- `A/n.java`

Key findings:

- Financial SMS identification and filtering logic.
- Historical inbox querying covering a recent 30-day period.
- HTTP-based SMS forwarding.
- Separate phone-number-based SMS forwarding.
- Remote SMS transmission through Android's `SmsManager`.
- SMS broadcast receiver functionality.
- SMS delivery and retry-handling logic.

**Outcome:** Multiple distinct SMS-related code paths documented.

### Phase 5 — Firebase and Remote Command Examination

**Date:** Not recorded  
**Activity:** FCM implementation analysis

The investigation examined `MyFirebaseMessagingService.java` and associated service implementations.

The following command handlers were identified:

- `ONLINE_CHECK`
- `SYNC_DEVICE`
- `PING`
- `SEND_SMS`
- `GET_SMS`
- `RUN_USSD`

Firebase project configuration and FCM token registration logic were also examined.

**Outcome:** Remote command-handling architecture documented. Actual command delivery and execution were not established.

### Phase 6 — Device Information Collection Analysis

**Date:** Not recorded  
**Activity:** Background service Smali examination

The background service was examined at Smali level because the corresponding JADX source decompilation was incomplete.

The analysis identified HTTP POST functionality involving:

- Device name and model.
- Android device identifier.
- SIM carrier information.
- SIM phone numbers.
- Creation and last-seen timestamps.
- Online status.
- Battery information.

The configured endpoint was identified as:

```text
https://w60.kinginfo.online/background_service.php
```

**Outcome:** Device information collection and transmission implementation documented.

### Phase 7 — Call-Forwarding and USSD Analysis

**Date:** Not recorded  
**Activity:** Telephony functionality examination

The investigation examined:

- `CallService.java`
- `UssdService.java`
- FCM `RUN_USSD` command handling.

The analysis identified:

- Remote call-forwarding configuration retrieval.
- SIM-slot selection.
- USSD command construction.
- Android telephony API usage.
- USSD status and response reporting.

Identified command patterns:

| Operation | Command pattern |
|---|---|
| Enable call forwarding | `**21*<number>#` |
| Disable call forwarding | `##21#` |

**Outcome:** Remote telephony-related functionality documented. Carrier-side execution was not verified.

### Phase 8 — Persistence and Native Anti-Analysis Examination

**Date:** Not recorded  
**Activity:** Background service and native library analysis

The investigation examined boot-related service initialization, SMS broadcast receivers and background execution mechanisms.

The native library `libzwdwbxqi.so` was also examined.

Identified JNI exports included:

- `getSecretKey`
- `nativeXorChunk`
- `getTargetPackage`
- `nativeScanEnv`

The native inspection identified checks associated with Frida, Xposed, Substrate, Gadget indicators, process memory maps, debugger tracing and instrumentation-related ports.

**Outcome:** Background execution and native anti-analysis indicators documented.

### Phase 9 — C2 Configuration Extraction

**Date:** Not recorded  
**Activity:** Application configuration analysis

The application's `server.json` configuration was examined to identify remote endpoints.

The investigation identified references to:

```text
w60.kinginfo.online
host.kinginfo.online
w60.mrkinginfoback.online
```

Endpoint references were correlated with relevant Java and Smali functionality wherever possible.

Firebase project configuration was also recorded.

**Outcome:** Configured remote infrastructure and associated functionality documented.

### Phase 10 — Domain Registration and DNS Intelligence

**Date:** 2026-11-03  
**Recorded DNS observation:** 14:49:33 UTC

DNS and domain registration intelligence was collected for the identified infrastructure.

The investigation examined:

- A records.
- AAAA records.
- RDAP registration information.
- Nameserver information.
- Registrar details.
- Available entity and abuse-contact information.

Cloudflare edge resolution was observed for `w60.kinginfo.online` and `host.kinginfo.online`.

Observed IPv4 addresses:

```text
104.21.3.189
172.67.131.27
```

Observed IPv6 addresses:

```text
2606:4700:3031::6815:3bd
2606:4700:3037::ac43:831b
```

**Outcome:** DNS and registration observations documented. Cloudflare addresses were classified as edge addresses, not confirmed origin IPs.

### Phase 11 — TLS and Certificate Transparency Examination

**Date:** Not recorded  
**Activity:** Certificate intelligence analysis

TLS certificates and Certificate Transparency observations were examined for infrastructure-related context.

The collected Cert Spotter dataset contained:

| Metric | Result |
|---|---:|
| Total records | 229 |
| Unique certificate IDs | 229 |
| Unique DNS names | 167 |
| Hostname-certificate records | 180 |
| Unique numbered `w` hostnames | 143 |

The analysis included certificate issuance dates, expiry dates, public-key fingerprints and hostname relationships.

The collected dataset was not exhaustive.

**Outcome:** Certificate lifecycle and hostname observations documented without making unsupported ownership or threat attribution claims.

### Phase 12 — HTTP Endpoint Response Audit

<badge color="info">Recorded event</badge>

**Date:** 2026-11-04  
**Timestamp:** 13:02:38 UTC

An endpoint response audit was conducted against configured application endpoints.

Recorded observations:

- Twelve endpoints returned HTTP 200.
- `w60.mrkinginfoback.online/update_call_forward.php` failed DNS resolution.
- Cloudflare response headers were observed.
- Google Trust Services was observed as the TLS certificate issuer.
- HSTS was observed with `max-age=31536000`.
- Multiple Cloudflare edge identifiers were recorded.

One endpoint returned a JSON response containing a forwarding number and status `off`.

The personal information was redacted from public documentation.

**Outcome:** Endpoint response observations recorded. HTTP 200 was not interpreted as proof of successful backend processing or data storage.

### Phase 13 — Investigation Consolidation

**Date:** 2026-11-04  
**Activity:** Investigation closure and documentation planning

The investigation reached its documentation and consolidation phase.

The following activities were undertaken:

- Consolidation of APK analysis findings.
- Consolidation of C2 infrastructure observations.
- Review of evidence classifications.
- Documentation of unresolved questions.
- Separation of code-derived capabilities from unverified runtime behaviour.
- Preparation of a structured GitHub research repository.

Dynamic analysis remained outside the scope of this investigation phase.

**Outcome:** Investigation findings frozen at the documented evidence state for repository preparation.

### Phase 14 — GitHub Repository Documentation

**Date:** 2026-11-04  
**Activity:** Repository creation and documentation

A GitHub repository was created to organise and publish the investigation documentation.

The repository structure includes:

- Technical APK analysis.
- Investigation documentation.
- Infrastructure intelligence.
- IOC records.
- Evidence register.
- Chain-of-custody records.
- Consolidated investigation reports.
- Supporting scripts.

Mermaid diagrams were selected for architecture and investigation-flow visualisations.

**Outcome:** Structured documentation repository established.

---

## 3. Chronological Summary

| Phase | Activity | Recorded date |
|---|---|---|
| 1 | Primary APK identification | Not recorded |
| 2 | APK structural examination | Not recorded |
| 3 | Embedded APK recovery | Not recorded |
| 4 | SMS functionality analysis | Not recorded |
| 5 | Firebase and command analysis | Not recorded |
| 6 | Device information analysis | Not recorded |
| 7 | Call-forwarding and USSD analysis | Not recorded |
| 8 | Persistence and anti-analysis examination | Not recorded |
| 9 | C2 configuration extraction | Not recorded |
| 10 | DNS and RDAP intelligence | 2026-11-03 |
| 11 | TLS and certificate intelligence | Not recorded |
| 12 | HTTP endpoint response audit | 2026-11-04 |
| 13 | Investigation consolidation | 2026-11-04 |
| 14 | GitHub documentation | 2026-11-04 |

The order represents the reconstructed investigation workflow. It should not be interpreted as proof of exact execution order for phases whose timestamps were unavailable.

---

## 4. Important Recorded Timestamps

The following timestamps were explicitly available in the investigation records.

| Event | Timestamp (UTC) |
|---|---|
| `kinginfo.online` RDAP registration date | 2026-06-25 06:26 |
| Earliest certificate `not_before` in collected dataset | 2026-08-06 04:36:56 |
| DNS observation | 2026-11-03 14:49:33 |
| Endpoint response audit | 2026-11-04 13:02:38 |

**Note:** The RDAP registration date and certificate issuance dates describe infrastructure history. They are not dates on which this investigation necessarily performed those activities.

---

## 5. Timeline Integrity and Limitations

This timeline was reconstructed from available investigation notes and recorded observations.

The following principles apply:

- Dates are included only where supported by available records.
- Exact timestamps are not inferred from file names or undocumented assumptions.
- Historical domain registration and certificate dates are distinguished from investigation activity.
- Infrastructure observations are tied to their collection timestamps.
- Missing timestamps are explicitly marked as `Not recorded`.
- The phase ordering is a documentation reconstruction, not necessarily a precise operational chronology.

Where original terminal logs, command histories or analysis records provide additional timestamps, this document can be updated with those verified values.

---

## 6. Conclusion

The investigation progressed from primary APK identification through structural examination, reverse engineering, embedded APK recovery, capability analysis and infrastructure intelligence.

The recorded DNS and endpoint observations provided additional context about the application's configured remote infrastructure.

The investigation was consolidated on 4 November 2026, and the findings were organised into a structured GitHub documentation repository.

This timeline provides a chronological reference for the technical findings, evidence register and consolidated investigation reports.

---

## Related Documentation

- [Executive Summary](executive-summary.md)
- [Investigation Scope](investigation-scope.md)
- [Investigation Findings](findings.md)
- [Investigation Limitations](limitations.md)
- [Methodology](methodology.md)
- [Evidence Register](../evidence/evidence-register.md)
- [Chain of Custody](../evidence/chain-of-custody.md)
- [Static Analysis Report](../reports/static-analysis-report.md)
- [C2 Infrastructure Report](../reports/c2-infrastructure-report.md)

---

**Document:** Investigation Timeline  
**Project:** HDFC Android APK Investigation  
**Time Standard:** UTC  
**Status:** Reconstructed from available investigation records