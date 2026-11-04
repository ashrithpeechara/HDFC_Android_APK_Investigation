# Indicators of Compromise (IOCs)

## 1. Overview

This document provides a consolidated, human-readable catalogue of indicators identified during the Android APK and C2 infrastructure investigation.

The indicators are derived from:

- Primary and embedded APK artifacts.
- APK signing certificates.
- Application configuration files.
- Firebase configuration.
- Static code examination.
- DNS and domain intelligence.
- TLS and certificate-transparency observations.
- HTTP endpoint assessment.

The indicators are classified according to their type, origin, investigative relevance, and confidence.

**Important:** An indicator's presence in this repository does not automatically establish that it is malicious. Domain association, configuration references, and infrastructure observations must be interpreted in the context of the investigation.

## 2. Indicator Classification

| Classification | Meaning |
|---|---|
| Artifact indicator | Directly identifies an examined APK or its signing certificate |
| Configured infrastructure | Domain or URL recovered from application configuration |
| Observed infrastructure | Domain or infrastructure observed during passive assessment |
| Application identifier | Package name or Firebase identifier associated with the application |
| Contextual indicator | Supporting technical information useful for correlation |

### Confidence levels

| Confidence | Meaning |
|---|---|
| High | Directly recovered from an examined artifact or supported by a recorded observation |
| Medium | Supported by infrastructure observations but with attribution or operational uncertainty |
| Low | Limited contextual evidence; requires independent validation |

Confidence describes the strength of the observation, not proof of maliciousness.

## 3. Cryptographic Indicators

### 3.1 Primary APK

| Attribute | Indicator |
|---|---|
| Type | SHA-256 |
| Value | `08cfe1f957d7539320eaaa97f1d6838182f5df57e6f875d00dc3060e432d35af` |
| Associated artifact | Primary HDFC BANK LOAN SERVICE APK |
| Package | `com.sec.android.app.finance.kaxqj68` |
| Version | `2.9.65` |
| Confidence | High |
| Source | APK metadata examination |

### 3.2 Embedded APK

| Attribute | Indicator |
|---|---|
| Type | SHA-256 |
| Value | `13f93b8c70881f9414944fdc55811bfc627dbec966f023c664eb98782690cb4c` |
| Associated artifact | Decoded embedded APK |
| Package | `com.nxtwave.support` |
| Version | `1.0` |
| Confidence | High |
| Source | Embedded APK extraction and metadata examination |

### 3.3 APK signing certificate

| Attribute | Indicator |
|---|---|
| Type | Certificate SHA-256 |
| Value | `6215f00baa4bf18bab5792fc796bfc5555917240f14f7c7e672d956888d75c96` |
| Subject | `CN=editor` |
| Key algorithm | RSA 2048 |
| Associated artifacts | Primary APK and embedded APK |
| Confidence | High |
| Source | APK signing-certificate examination |

The shared signing certificate establishes a relationship between the two examined APK artifacts. It does not independently establish publisher identity or execution linkage.

## 4. Domain Indicators

The following domains and hostnames were recovered from application configuration or infrastructure assessment.

| Domain / Hostname | Indicator role | Classification | Confidence |
|---|---|---|---|
| `kinginfo.online` | Primary configured infrastructure domain | Configured infrastructure | High |
| `w60.kinginfo.online` | Application service hostname | Configured infrastructure | High |
| `host.kinginfo.online` | Configuration retrieval hostname | Configured infrastructure | High |
| `mrkinginfoback.online` | Secondary configured domain | Configured infrastructure | High |
| `w60.mrkinginfoback.online` | Call-forwarding update hostname | Configured infrastructure | High |

**Interpretation:** These domains are associated with the examined application's configuration. Their inclusion does not independently establish domain ownership, malicious hosting, or operator identity.

## 5. URL Indicators

### 5.1 Primary application endpoints

| URL | Configured function |
|---|---|
| `https://w60.kinginfo.online/background_service.php` | Device and background status reporting |
| `https://w60.kinginfo.online/sms_forward.php` | SMS forwarding |
| `https://w60.kinginfo.online/sms_forward_number.php` | SMS forwarding-number configuration |
| `https://w60.kinginfo.online/call_forward.php` | Call-forwarding-related operation |
| `https://w60.kinginfo.online/call_forward_setting.php` | Call-forwarding configuration |
| `https://w60.kinginfo.online/sms_send.php` | Remote SMS transmission |
| `https://w60.kinginfo.online/app_upload.php` | Application upload-related functionality |
| `https://w60.kinginfo.online/permission.php` | Permission configuration |
| `https://w60.kinginfo.online/save_token.php` | FCM token registration |
| `https://w60.kinginfo.online/web/api/check_online.php` | Online-status checking |
| `https://w60.kinginfo.online/ussd_setting.php` | USSD configuration |
| `https://w60.kinginfo.online/update_ussd.php` | USSD status reporting |

### 5.2 Additional endpoints

| URL | Configured function |
|---|---|
| `https://w60.mrkinginfoback.online/update_call_forward.php` | Call-forwarding status update |
| `https://host.kinginfo.online/get.php` | Web configuration retrieval |

These URLs were recovered from application configuration. Their actual application-level behaviour was not independently established for every endpoint.

## 6. Application Identifiers

| Indicator type | Value | Context |
|---|---|---|
| Android package | `com.sec.android.app.finance.kaxqj68` | Primary APK |
| Android package | `com.nxtwave.support` | Embedded APK |
| Firebase project ID | `fcmtoken-af5a6` | FCM integration |
| Firebase sender ID | `705898731` | Firebase configuration |
| Firebase App ID | `1:705898731153:web:130e5565c49b143bfb9130` | Firebase configuration |

These identifiers are useful for correlation and investigation. They are not standalone proof of maliciousness.

## 7. Certificate Indicators

### 7.1 `w60.kinginfo.online`

| Attribute | Value |
|---|---|
| Certificate ID | `17436230060` |
| Certificate SHA-256 | `63d72c5c9a96756ef7d88f6c2965d2b6962ab744dbae983159eafb1808b39321` |
| Public-key SHA-256 | `78439e520243b864cc5e082ed503d61fdbdbf67358b764c1f505e538d441a3ca` |
| Issuer | Let's Encrypt YR2 |
| Issued | 2026-09-27 |
| Expires | 2026-12-26 |

### 7.2 `host.kinginfo.online`

| Certificate ID | Public-key SHA-256 |
|---|---|
| `16807392801` | `4319b47dce7fac5770cb1c605aafa2d6a8cdf51ce027bf8820833b72cca74654` |
| `17970088057` | `81d0ade030edb4c739a49947d740a4abc419cad3cefd2f78765d1b5d555fd6ff` |

Certificate and public-key fingerprints are supporting infrastructure identifiers. They should not be treated as proof of malicious activity or common ownership.

## 8. Network Infrastructure Observations

The following addresses were returned during DNS assessment:

| Record | Address |
|---|---|
| A | `104.21.3.189` |
| A | `172.67.131.27` |
| AAAA | `2606:4700:3031::6815:3bd` |
| AAAA | `2606:4700:3037::ac43:831b` |

These addresses were identified as Cloudflare-associated edge addresses.

**Handling guidance:** Do not classify these IP addresses as confirmed origin servers or exclusive infrastructure belonging to the application operator. They may be shared CDN infrastructure.

## 9. Behavioural Indicators

The following code-derived behaviours are useful when conducting endpoint, device, or malware investigations.

| Behavioural indicator | Relevant component |
|---|---|
| Financial SMS filtering | `SmsService.java` |
| HTTP-based SMS forwarding | `SmsService.java` |
| SMS broadcast monitoring | `SmsForwardService.java`, `SmsReceiver.java` |
| Configurable SMS forwarding number | `A/n.java` |
| Remote SMS transmission | `SmsSendService.java` |
| FCM command dispatch | `MyFirebaseMessagingService.java` |
| FCM token registration | `A/n.java` |
| Device and SIM information reporting | `BackgroundService.smali` |
| Call-forwarding configuration | `CallService.java` |
| Remote USSD workflow | `UssdService.java` |
| Boot-triggered service startup | `BootReceiver` |
| Instrumentation detection | `libzwdwbxqi.so` |

These are behavioural indicators rather than unique file hashes or network signatures. They may assist analysts in identifying related functionality but are not sufficient alone to identify a specific malware family.

## 10. Sensitive Data Handling

The response from:

`https://w60.kinginfo.online/sms_forward_number.php`

contained a `forward_number` field and a `status` value of `off`.

The returned telephone number is intentionally excluded from this repository.

The original response should remain in restricted investigation evidence storage. It must not be published in:

- Public IOC feeds.
- GitHub commits.
- Screenshots.
- Public reports.
- Unredacted CSV or JSON files.

The identity and role of the returned number were not established.

## 11. IOC Validation and Operational Guidance

Before using an indicator in a production detection or blocking rule:

1. Verify the indicator against the original evidence.
2. Confirm that its value has not been altered during transcription.
3. Check its current reputation using appropriate threat-intelligence sources.
4. Distinguish shared hosting and CDN infrastructure from dedicated infrastructure.
5. Consider false-positive risks.
6. Record the date and source of any subsequent validation.
7. Preserve the original investigation context.

### Suggested defensive use

| Indicator category | Potential defensive use |
|---|---|
| APK SHA-256 | File identification and endpoint detection |
| Certificate SHA-256 | Signing-certificate correlation |
| Configured domains | DNS and proxy monitoring |
| Configured URLs | Web proxy and network telemetry correlation |
| Package identifiers | Android application inventory review |
| Firebase project identifier | Application configuration correlation |
| Behavioural indicators | Static detection and threat hunting |

Blocking a shared Cloudflare IP address is not recommended solely because it appeared in this investigation.

## 12. Investigation Limitations

- No dynamic application execution was performed.
- Successful data exfiltration was not established.
- FCM command delivery was not established.
- Successful call-forwarding or USSD execution was not established.
- Server-side storage was not established.
- Infrastructure operator attribution was not established.
- Cloudflare edge addresses were not verified as origin IPs.
- Certificate-transparency collection was incomplete.
- No malware-family attribution was established.

## 13. Conclusion

This IOC catalogue consolidates artifact hashes, signing-certificate fingerprints, configured domains and URLs, application identifiers, certificate observations, network addresses, and code-derived behavioural indicators.

The strongest artifact identifiers are the two APK SHA-256 hashes and their shared signing-certificate fingerprint.

The configured infrastructure indicators are directly associated with the examined application's configuration, but malicious ownership and operational impact remain unverified.

All indicators should be interpreted with their evidence context and confidence level before operational deployment.

**Classification:** Suspicious Android application and associated configured infrastructure  
**Attribution:** Undetermined  
**Runtime impact:** Not established  
**Dynamic analysis:** Not performed