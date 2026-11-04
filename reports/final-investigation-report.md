# Final Digital Investigation Report
## Android Application Security and C2 Infrastructure Investigation

---

## 1. Executive Summary

A forensic and security-oriented static investigation was conducted on an Android application displaying the label **HDFC BANK LOAN SERVICE**.

The examination identified a suspicious Android application containing multiple code-derived capabilities associated with sensitive SMS processing, remote SMS transmission, Firebase Cloud Messaging (FCM)-based command handling, call-forwarding manipulation, USSD operations, device information reporting, and native anti-analysis checks.

An additional Android application package was recovered from an encrypted asset embedded within the primary APK.

The primary application contains a configuration-driven communication architecture referencing multiple remote endpoints under `kinginfo.online`, along with a secondary domain under `mrkinginfoback.online` and a configuration endpoint under `host.kinginfo.online`.

The investigation also examined DNS records, domain-registration information, TLS certificates, certificate-transparency observations, and HTTP endpoint responses.

### Principal findings

1. The application contains code for filtering financial and banking-related SMS messages and forwarding message data through HTTP requests.
2. A separate mechanism can retrieve a forwarding number and status from remote configuration and use Android SMS functionality to forward message content.
3. Remote SMS transmission functionality is implemented through `SmsSendService`.
4. FCM command handlers include operations associated with SMS retrieval, SMS transmission, device synchronisation, online status, and USSD execution.
5. Call-forwarding configuration can trigger USSD operations intended to enable or disable call forwarding.
6. Device and SIM-related information is included in a background reporting implementation.
7. A native ARM64 library contains checks associated with Frida, Xposed, Substrate, instrumentation, and debugging environments.
8. A secondary APK was recovered from an encrypted asset and shares the primary APK's signing certificate.
9. Multiple configured remote endpoints returned HTTP 200 responses during the recorded endpoint audit.
10. A response from the SMS forwarding-number endpoint exposed a telephone-number field and a forwarding status of `off`. The actual number is redacted from this public report.

### Overall assessment

The examined application is classified as **highly suspicious and potentially capable of unauthorised access to sensitive communications and telephony operations**.

The displayed HDFC Bank branding has not been independently verified as authorised.

This investigation was based on static APK analysis and passive infrastructure observations. It does not establish successful execution on a victim device, actual data exfiltration, successful telephony manipulation, server-side data storage, financial loss, or operator attribution.

---

## 2. Investigation Information

| Attribute | Details |
|---|---|
| Investigation title | Android APK and C2 Infrastructure Investigation |
| Primary artifact | HDFC BANK LOAN SERVICE APK |
| Primary package | `com.sec.android.app.finance.kaxqj68` |
| Application version | `2.9.65` |
| Secondary package | `com.nxtwave.support` |
| Analysis category | Android application security and digital forensics |
| Primary examination | Static APK analysis |
| Supporting examination | Smali inspection and configuration analysis |
| Infrastructure assessment | Passive DNS, TLS, certificate and endpoint observations |
| Dynamic analysis | Not performed |
| Attribution | Undetermined |
| Victim impact | Not established |

## 3. Investigation Objectives

The investigation was designed to establish the identity and security characteristics of the supplied Android application.

The objectives were:

- Identify the APK's package metadata and cryptographic identity.
- Examine application permissions and Android components.
- Identify sensitive SMS-related functionality.
- Examine FCM configuration and command handling.
- Investigate call-forwarding and USSD operations.
- Identify persistence and background-service mechanisms.
- Examine native anti-analysis functionality.
- Recover and identify embedded application artifacts.
- Extract configured remote infrastructure.
- Assess DNS, TLS, certificate and HTTP observations.
- Document findings in a reproducible technical repository.

## 4. Investigation Scope

### 4.1 Included activities

The investigation included:

- APK metadata examination.
- SHA-256 hashing.
- APK signing-certificate inspection.
- Embedded APK identification and decoding.
- Manifest and permission examination.
- Java decompilation and Smali inspection.
- Application configuration extraction.
- Static examination of SMS and telephony functionality.
- Firebase configuration examination.
- Native library inspection.
- Passive domain and DNS intelligence.
- TLS and certificate-transparency observations.
- HTTP endpoint response assessment.
- Evidence documentation and report preparation.

### 4.2 Excluded activities

The following activities were outside the completed investigation scope:

- Dynamic APK execution.
- Live Android device experimentation.
- Controlled network traffic capture during application execution.
- Exploitation of remote infrastructure.
- Backend source-code analysis.
- Database extraction from remote infrastructure.
- Victim-device forensic acquisition.
- Operator identification or attribution.

These exclusions are important when interpreting the findings.

---

## 5. Examined Artifacts

### 5.1 Primary APK

| Attribute | Value |
|---|---|
| Application label | `HDFC BANK LOAN SERVICE` |
| Package name | `com.sec.android.app.finance.kaxqj68` |
| Version | `2.9.65` |
| Minimum SDK | 24 |
| Target SDK | 37 |
| Signing certificate subject | `CN=editor` |
| Signing key | RSA 2048 |
| SHA-256 | `08cfe1f957d7539320eaaa97f1d6838182f5df57e6f875d00dc3060e432d35af` |
| Certificate SHA-256 | `6215f00baa4bf18bab5792fc796bfc5555917240f14f7c7e672d956888d75c96` |

### 5.2 Embedded APK

The primary APK contained an asset named `rmtley9lr.db`.

The asset was identified as an APK protected using a repeating-XOR transformation. After decoding, the resulting package was examined separately.

| Attribute | Value |
|---|---|
| Original asset | `rmtley9lr.db` |
| Recovered package | `com.nxtwave.support` |
| Version | `1.0` |
| Minimum SDK | 25 |
| Target SDK | 34 |
| SHA-256 | `13f93b8c70881f9414944fdc55811bfc627dbec966f023c664eb98782690cb4c` |
| Signing certificate | Same as primary APK |

The recovered APK passed ZIP integrity testing and contained 986 entries.

Unusual absolute-style and backslash path formatting was observed. These observations alone do not establish path traversal.

The shared signing certificate establishes a certificate relationship between the artifacts, not proof of execution or installation of the embedded package.

---

## 6. Technical Findings

### 6.1 Financial SMS filtering and HTTP forwarding

<badge color="danger">High concern</badge>

The investigation identified financial-message filtering functionality in `SmsService.java`.

The filtering logic includes patterns associated with:

- Banking institutions.
- Account and balance notifications.
- Transaction and credit notifications.
- UPI and payment-related messages.
- Wallet and payment applications.

The method `b(String)` performs message filtering.

The method `c(...)` constructs an HTTP POST request to the configured `sms_forward_url`.

The request includes fields such as:

| Field | Purpose |
|---|---|
| `device_id` | Device identifier |
| `sender` | Message sender |
| `user_number` | User number field |
| `message` | SMS body |
| `timestamp` | Message timestamp |
| `type` | Message category |
| `part_number` | Multipart message part |
| `total_parts` | Total multipart message parts |

**Assessment:** The code contains functionality capable of transmitting sensitive financial SMS content to configured remote infrastructure.

Successful server-side receipt or storage was not established.

### 6.2 Separate SMS forwarding mechanism

<badge color="danger">High concern</badge>

A separate forwarding workflow was identified across:

- `SmsForwardService.java`
- `SmsReceiver.java`
- `A/n.java`

The service registers for Android SMS-received broadcasts. The configuration logic periodically retrieves a forwarding number and status from `sms_forward_number.php`.

When the returned status is `on`, the code uses `SmsManager` to forward the message body to the configured number.

Previously stored preferences may be used when network connectivity is unavailable.

**Assessment:** The application contains a second SMS forwarding mechanism, separate from the HTTP-based financial SMS forwarding path.

Actual delivery to a telephone number was not verified.

### 6.3 Remote SMS transmission

<badge color="danger">High concern</badge>

`SmsSendService.java` implements remote SMS transmission functionality.

The identified implementation includes:

- Retrieval of the configured SMS sending endpoint.
- Device identifier collection.
- SIM/subscription selection.
- `SmsManager.sendTextMessage`.
- `SmsManager.sendMultipartTextMessage`.
- SMS-sent and SMS-delivered broadcast handling.
- Retry logic with up to three retries.

The FCM command `SEND_SMS` can start this service.

**Assessment:** The code supports remotely initiated SMS transmission. Actual command delivery and successful message transmission were not established.

### 6.4 Firebase Cloud Messaging command handling

<badge color="danger">High concern</badge>

`MyFirebaseMessagingService.java` contains command-dispatch functionality.

| Command | Code-derived operation |
|---|---|
| `ONLINE_CHECK` | Online-state update |
| `SYNC_DEVICE` | Device synchronisation |
| `PING` | Online-state update |
| `SEND_SMS` | Starts `SmsSendService` |
| `GET_SMS` | Starts `SmsService` with latest-SMS retrieval flag |
| `RUN_USSD` | Starts `UssdService` |

The application also contains FCM token registration functionality.

**Assessment:** FCM provides a potential remote command channel for sensitive application operations.

No evidence establishes that a remote operator actually delivered commands to an application instance.

### 6.5 Device information reporting

<badge color="warning">Medium–high concern</badge>

`BackgroundService.smali` contains an implementation that constructs HTTP POST requests to the configured background-service endpoint.

The request includes:

- Device name and model.
- Device identifier.
- SIM carrier information.
- SIM number fields.
- Creation and last-seen timestamps.
- Online status.
- Battery information.

The corresponding JADX source was incomplete, so Smali inspection was used.

**Assessment:** The implementation contains device and SIM information reporting functionality.

Successful server-side receipt or storage was not established.

### 6.6 Call-forwarding manipulation

<badge color="danger">High concern</badge>

`CallService.java` retrieves remote call-forwarding configuration.

The observed operations include:

| Remote state | USSD operation |
|---|---|
| `on` | `**21*<number>#` |
| `off` | `##21#` |

The implementation uses subscription-specific `TelephonyManager.sendUssdRequest(...)` functionality.

It also contains logic for reporting the result to the configured update endpoint.

**Assessment:** The application contains code intended to manipulate call-forwarding settings.

Carrier acceptance and successful call redirection were not verified.

### 6.7 USSD command workflow

<badge color="danger">High concern</badge>

The FCM command handler can dispatch `RUN_USSD` to `UssdService.java`.

The service processes command-related values and uses the configured update endpoint to report:

- Device identifier.
- Command identifier.
- USSD code.
- SIM slot.
- Status.
- Response.
- Error information.

The exact `UssdService.onStartCommand()` invocation path was not fully recovered through JADX and would require further Smali verification.

**Assessment:** A remote USSD workflow is present in the application. Successful execution was not established.

### 6.8 Persistence and background services

<badge color="warning">Medium–high concern</badge>

The investigation identified:

- A `BootReceiver` that starts `SmsForwardService`.
- SMS-related service startup from `MainActivity` after permission handling.
- SMS broadcast registration.
- Shared-preference storage of forwarding configuration and status.

**Assessment:** The application contains mechanisms intended to restore or maintain selected background functionality.

Successful persistence across actual device reboots was not tested.

### 6.9 Native anti-analysis checks

<badge color="warning">Medium–high concern</badge>

The primary APK contains the stripped ARM64 native library:

`libzwdwbxqi.so`

Identified JNI functions include:

- `getSecretKey`
- `nativeXorChunk`
- `getTargetPackage`
- `nativeScanEnv`

The native environment scan checks for references associated with:

- Frida.
- Xposed.
- Substrate.
- Gadget.
- Frida/Gum threads.
- TCP ports `27042` and `27043`.
- The process `TracerPid` value.

**Assessment:** The library contains checks consistent with instrumentation and debugging-environment detection.

Their runtime effect was not tested.

---

## 7. C2 Infrastructure Assessment

### 7.1 Primary domain

`kinginfo.online`

The primary application configuration references multiple endpoints under:

`w60.kinginfo.online`

The configured operations include:

- Device status reporting.
- SMS forwarding.
- SMS forwarding configuration.
- Remote SMS transmission.
- Call-forwarding configuration.
- USSD configuration and reporting.
- FCM token registration.
- Permission configuration.
- Application upload-related functionality.

### 7.2 Additional infrastructure

| Domain | Observed role |
|---|---|
| `kinginfo.online` | Primary configured service domain |
| `w60.kinginfo.online` | Main application endpoint hostname |
| `host.kinginfo.online` | Web configuration endpoint |
| `mrkinginfoback.online` | Secondary configured domain |
| `w60.mrkinginfoback.online` | Call-forwarding update hostname |

### 7.3 Firebase configuration

| Attribute | Value |
|---|---|
| Project ID | `fcmtoken-af5a6` |
| Sender ID | `705898731` |
| App ID | `1:705898731153:web:130e5565c49b143bfb9130` |
| API key | Redacted |

No Firebase Realtime Database URL was recovered.

### 7.4 DNS observations

RDAP information for `kinginfo.online` recorded:

- Registration date: 2026-06-25 06:26 UTC.
- Expiration date: 2027-06-25.
- Registrar: PDR Ltd / PublicDomainRegistry.
- Nameservers: `anna.ns.cloudflare.com` and `robert.ns.cloudflare.com`.

Observed DNS addresses for primary subdomains included:

- `104.21.3.189`
- `172.67.131.27`
- `2606:4700:3031::6815:3bd`
- `2606:4700:3037::ac43:831b`

These are Cloudflare-associated edge addresses, not verified origin IP addresses.

### 7.5 TLS and certificate observations

The endpoint audit recorded TLS certificates issued by Google Trust Services, Cloudflare server headers, and HSTS with `max-age=31536000`.

Cert Spotter collection produced:

| Attribute | Result |
|---|---:|
| Total collected records | 229 |
| Unique certificate IDs | 229 |
| Unique DNS names | 167 |
| Numbered `w` hostnames | 143 |
| Repeated hostnames with two records | 37 |

The observed certificate renewal pattern was approximately 58.73 days on average for the repeated hostname records.

The collection was incomplete and does not establish ownership or malicious activity.

### 7.6 Endpoint audit

The recorded endpoint audit timestamp was:

`2026-11-04 13:02:38 UTC`

HTTP 200 responses were observed for 12 configured endpoints.

The `w60.mrkinginfoback.online/update_call_forward.php` hostname returned a DNS resolution error.

HTTP 200 responses establish protocol-level responses, not successful application operations or server-side data storage.

### 7.7 Sensitive response observation

The endpoint:

`https://w60.kinginfo.online/sms_forward_number.php`

returned JSON containing:

- A `forward_number` field.
- A `status` field with value `off`.

The telephone number is redacted from this report.

This response raises a potential sensitive-configuration exposure concern. The identity of the number's owner, its association with any device, and the endpoint's intended access policy remain unknown.

---

## 8. Consolidated Risk Assessment

| Finding | Potential severity | Static evidence confidence |
|---|---|---|
| Financial SMS filtering and HTTP forwarding | High | High |
| Separate SMS forwarding mechanism | High | High |
| Remote SMS transmission | High | High |
| FCM remote command dispatch | High | High |
| Device and SIM information reporting | Medium–High | High |
| Call-forwarding manipulation | High | High |
| Remote USSD workflow | High | Medium–High |
| Boot-triggered service functionality | Medium–High | High |
| Native anti-analysis checks | Medium–High | High |
| Embedded secondary APK | Requires separate assessment | High |
| Sensitive forwarding configuration response | Potential information disclosure | Medium |

The severity ratings represent potential consequences if the relevant code paths execute successfully. They are not measurements of confirmed victim impact.

## 9. Evidence and Confidence Assessment

The investigation uses the following evidence categories:

| Evidence category | Definition |
|---|---|
| Direct artifact observation | Data directly recovered from an APK or configuration file |
| Code-derived capability | Functionality represented in Java or Smali implementation |
| Infrastructure observation | DNS, TLS, HTTP, RDAP, or certificate information collected during assessment |
| Runtime-confirmed behaviour | Behaviour reproduced through controlled application execution |

### 9.1 Evidence summary

| Claim | Evidence category | Established? |
|---|---|---|
| Primary APK package identity | Direct artifact observation | Yes |
| Embedded APK identity | Direct artifact observation | Yes |
| SMS forwarding request construction | Code-derived capability | Yes |
| FCM command dispatch implementation | Code-derived capability | Yes |
| Call-forwarding USSD implementation | Code-derived capability | Yes |
| Native instrumentation checks | Code-derived capability | Yes |
| Configured remote endpoint references | Direct artifact observation | Yes |
| HTTP 200 endpoint responses | Infrastructure observation | Yes |
| Actual FCM command delivery | Runtime-confirmed behaviour | No |
| Successful SMS exfiltration | Runtime-confirmed behaviour | No |
| Successful call redirection | Runtime-confirmed behaviour | No |
| Server-side data storage | Independent backend evidence | No |
| Victim impact | Device or incident evidence | Not established |
| Operator attribution | Independent attribution evidence | Not established |

---

## 10. Investigation Timeline

The following is a high-level sequence of investigation activities. It is not a complete timestamped event chronology.

1. Primary APK identity and metadata examination.
2. Cryptographic hashing and signing-certificate assessment.
3. Embedded asset identification and secondary APK recovery.
4. Permission and Android component examination.
5. SMS filtering and forwarding analysis.
6. FCM command-handling analysis.
7. Call-forwarding and USSD code examination.
8. Background service and persistence analysis.
9. Native anti-analysis examination.
10. Remote endpoint extraction and classification.
11. Firebase configuration analysis.
12. DNS and domain intelligence collection.
13. TLS and certificate-transparency assessment.
14. HTTP endpoint response assessment.
15. Evidence documentation and report preparation.

Refer to `docs/timeline.md` for the detailed investigation timeline.

---

## 11. Limitations and Unresolved Questions

The following questions remain outside the established evidence:

1. Does the application execute all identified functionality on a supported Android device?
2. Are remote FCM commands delivered to a specific application instance?
3. Does the backend successfully store received SMS or device information?
4. Are call-forwarding operations accepted by the relevant mobile carrier?
5. Does the embedded APK have an execution or installation relationship with the primary APK?
6. Who operates the configured infrastructure?
7. Is the displayed HDFC Bank branding authorised?
8. Was any individual device or financial account actually affected?

These questions must not be answered through speculation.

The investigation did not include dynamic analysis, backend access, or victim-device acquisition.

---

## 12. Defensive Recommendations

For organisations and individuals who encounter this application:

### 12.1 Application handling

- Do not install or execute the APK on a personal or operational device.
- Preserve the original APK.
- Record and verify its SHA-256 hash.
- Retain the source URL, submission context, and relevant timestamps.
- Use isolated analysis environments for any separately authorised dynamic assessment.

### 12.2 If installation is suspected

- Initiate an appropriate incident-response process.
- Preserve relevant device evidence before making changes.
- Review SMS and telephony-related permissions.
- Examine call-forwarding settings through the mobile carrier or trusted device settings.
- Review unexpected SMS activity.
- Contact financial institutions through independently verified official channels if financial compromise is suspected.

### 12.3 Organisational response

- Share verified indicators with authorised security teams.
- Preserve evidence and chain-of-custody records.
- Report suspected brand impersonation through official reporting channels.
- Avoid direct interaction with suspicious infrastructure unless explicitly authorised.
- Do not treat Cloudflare edge IPs as confirmed origin infrastructure.

---

## 13. Final Assessment

The investigation identified a highly suspicious Android application presenting itself as `HDFC BANK LOAN SERVICE`.

The primary APK contains multiple sensitive capabilities involving financial SMS filtering, SMS forwarding, remote SMS transmission, FCM-based command dispatch, device information reporting, call-forwarding manipulation, USSD operations, background services, and native anti-analysis checks.

The recovery of a second APK from an encrypted asset provides an additional artifact for examination.

The application's configuration references a multi-endpoint remote infrastructure architecture, and passive assessment recorded responses from multiple configured endpoints.

The combination of these findings raises significant concerns regarding the application's potential impact on communication confidentiality and telephony integrity.

However, the evidence does not establish successful execution, actual data exfiltration, victim compromise, financial loss, server-side storage, or operator identity.

**Final classification: Highly suspicious Android application with code-derived capabilities consistent with potentially unauthorised remote access to sensitive communications and telephony operations.**

**Attribution: Undetermined.**

**Victim impact: Not established.**

**Dynamic analysis: Not performed.**

---

## 14. Repository Documentation Index

### Reports

- `reports/static-analysis-report.md`
- `reports/c2-infrastructure-report.md`
- `reports/final-investigation-report.md`

### Analysis

- `analysis/apk-metadata.md`
- `analysis/permissions-analysis.md`
- `analysis/sms-analysis.md`
- `analysis/fcm-analysis.md`
- `analysis/call-forwarding-analysis.md`
- `analysis/ussd-analysis.md`
- `analysis/persistence-analysis.md`
- `analysis/anti-analysis.md`

### Infrastructure

- `infrastructure/dns-analysis.md`
- `infrastructure/domain-intelligence.md`
- `infrastructure/endpoint-observations.md`
- `infrastructure/firebase-analysis.md`
- `infrastructure/tls-analysis.md`

### Evidence

- `evidence/evidence-register.md`
- `evidence/chain-of-custody.md`

### Indicators

- `iocs/domains.json`
- `iocs/hashes.json`
- `iocs/indicators.csv`
- `iocs/indicators.md`

### Diagrams

- `diagrams/investigation-workflow.md`
- `diagrams/application-architecture.md`
- `diagrams/sms-forwarding-flow.md`
- `diagrams/fcm-command-flow.md`
- `diagrams/call-forwarding-flow.md`
- `diagrams/ussd-command-flow.md`
- `diagrams/c2-infrastructure-map.md`
- `diagrams/evidence-lifecycle.md`
- `diagrams/certificate-timeline.md`

---

## 15. Report Disclaimer

This report documents technical observations made during a static Android application and infrastructure investigation.

The conclusions are limited to the artifacts and observations available during the examination.

The report does not constitute proof of infection, successful data exfiltration, financial fraud, malicious infrastructure ownership, or criminal attribution.

All indicators and findings should be independently validated before operational use.

**Report status:** Final static investigation report  
**Investigation scope:** Static APK analysis and passive infrastructure assessment  
**Dynamic analysis:** Not performed  
**Attribution:** Undetermined  
**Victim impact:** Not established