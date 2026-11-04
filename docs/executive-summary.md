# Executive Summary

## 1. Case Overview

This document presents the executive summary of an independent security investigation involving a suspicious Android application labelled **HDFC BANK LOAN SERVICE**.

The investigation examined the application's internal structure, code-derived functionality, embedded APK, remote command-handling mechanisms, Firebase Cloud Messaging (FCM) integration and associated command-and-control (C2) infrastructure.

The primary objective was to identify potentially malicious capabilities, understand the application's communication architecture and document relevant technical indicators.

The investigation was conducted through static APK analysis, reverse engineering and passive infrastructure intelligence.

**Investigation approach:** Static analysis and infrastructure intelligence.

**Dynamic analysis:** Not performed.

## 2. Application Identification

The primary application was identified with the following attributes:

| Attribute | Value |
|---|---|
| Application label | HDFC BANK LOAN SERVICE |
| Package name | `com.sec.android.app.finance.kaxqj68` |
| Version | `2.9.65` |
| Minimum SDK | 24 |
| Target SDK | 37 |
| Signing certificate CN | `editor` |
| Signing algorithm | RSA 2048 |
| SHA-256 | `08cfe1f957d7539320eaaa97f1d6838182f5df57e6f875d00dc3060e432d35af` |

An additional APK was recovered from an encrypted application asset and analysed separately.

Its package name was identified as `com.nxtwave.support`.

## 3. Executive Findings

Static examination identified several security-sensitive capabilities within the primary application's code.

### 3.1 SMS Collection and Forwarding

The application contains logic to identify financial and transaction-related SMS messages.

The examined implementation includes:

- Financial SMS filtering using predefined patterns.
- Historical inbox querying covering a recent 30-day period.
- HTTP-based transmission of SMS information.
- A separate SMS forwarding mechanism using a remotely configured phone number.
- Remote SMS sending functionality through Android's `SmsManager` API.

These capabilities could expose sensitive financial communications if successfully executed with the required permissions.

### 3.2 Remote Command Handling

Firebase Cloud Messaging integration contains handlers for several remote commands:

- `ONLINE_CHECK`
- `SYNC_DEVICE`
- `PING`
- `SEND_SMS`
- `GET_SMS`
- `RUN_USSD`

The handlers demonstrate code paths capable of initiating device operations in response to corresponding messages.

Actual FCM command delivery and successful execution were not established.

### 3.3 Device Information Collection

The application's background service contains HTTP POST functionality for transmitting device-related information.

The examined fields include:

- Device name and model.
- Android device identifier.
- SIM carrier information.
- SIM phone numbers.
- Device creation and last-seen timestamps.
- Online status.
- Battery information.

The presence of transmission logic does not establish successful server-side receipt or storage.

### 3.4 Call Forwarding and USSD Operations

The application contains functionality associated with remote call-forwarding configuration.

The examined code constructs USSD commands for enabling and disabling call forwarding and uses Android's telephony APIs to submit requests.

A separate USSD service accepts remote command parameters and reports execution status to a configured endpoint.

Successful carrier-side execution was not verified.

### 3.5 Persistence and Anti-Analysis

The application includes boot-related and background service mechanisms.

Its native ARM64 library also contains checks associated with:

- Frida instrumentation.
- Xposed.
- Substrate.
- Gadget-related indicators.
- Debugger tracing.
- Process memory maps.
- Instrumentation-related network ports.

These findings indicate anti-analysis functionality in the examined native code. Runtime effectiveness was not evaluated.

### 3.6 Remote Infrastructure

The application configuration references multiple remote PHP endpoints under the following domains:

- `w60.kinginfo.online`
- `host.kinginfo.online`
- `w60.mrkinginfoback.online`

Infrastructure examination included DNS resolution, domain registration information, TLS certificates, Certificate Transparency observations and HTTP endpoint responses.

Some configured endpoints returned HTTP 200 during the observation period. This confirms endpoint responses at the time of collection, not successful execution of the application's operations.

## 4. Technical Assessment

The combination of financial SMS filtering, remote SMS operations, device information reporting, FCM command handling and telephony-related functionality represents a significant security concern.

The application's apparent association with an established financial institution also raises concerns about potential financial-service impersonation.

Based on the available static evidence, the application is assessed as:

**Highly suspicious — potentially unauthorised financial-service impersonation software with sensitive device-operation capabilities.**

This is an investigative assessment. It is not an official determination by HDFC Bank, proof of victim compromise or attribution to a particular threat actor.

## 5. Investigation Evidence and Confidence

| Finding | Evidence basis | Assessment |
|---|---|---|
| Financial SMS filtering | Decompiled Java code | High confidence in code presence |
| Historical SMS query | Decompiled code | High confidence in code presence |
| HTTP SMS forwarding | Decompiled Java code | High confidence in code presence |
| FCM command handlers | Decompiled Java code | High confidence in code presence |
| Device information reporting | Smali inspection | High confidence in code presence |
| Call-forwarding functionality | Decompiled Java code | High confidence in code presence |
| Native anti-analysis checks | Native library inspection | High confidence in code presence |
| C2 configuration | Application configuration files | High confidence in configured values |
| Endpoint responses | HTTP observations | Confirmed for collection period |
| Successful data exfiltration | No runtime evidence | Not established |
| Successful remote command execution | No runtime evidence | Not established |
| Operator identity | No attribution evidence | Unknown |

*Confidence in code presence must not be interpreted as confidence in successful execution or real-world impact.*

## 6. Investigation Limitations

The following limitations apply:

1. Dynamic analysis was not performed.
2. No live victim-device acquisition was conducted as part of this investigation.
3. Successful SMS exfiltration was not demonstrated.
4. Successful remote SMS transmission was not demonstrated.
5. Successful call forwarding or USSD execution was not demonstrated.
6. FCM command delivery was not established.
7. Server-side receipt or storage of collected information was not established.
8. Infrastructure ownership and operator attribution remain unverified.
9. Execution or installation of the embedded APK by the primary application was not established.

These limitations are important when interpreting the findings and assessing potential impact.

## 7. Recommended Defensive Actions

Based on the identified capabilities, the following defensive measures are recommended:

- Treat the APK as suspicious and avoid installation on personal or production devices.
- Preserve the original APK and calculate its SHA-256 hash.
- If the application is identified on a device, preserve relevant device evidence before remediation where legally and operationally appropriate.
- Review SMS, accessibility, notification, phone and other sensitive permissions.
- Examine unexpected call-forwarding configurations with the mobile network operator.
- Preserve relevant network and application logs.
- Share verified indicators with appropriate security teams and authorised threat-intelligence channels.
- Submit the findings through the financial institution's official security or fraud-reporting process.

## 8. Conclusion

The investigation identified multiple sensitive Android capabilities and a configured remote infrastructure architecture within the examined application.

The most significant findings concern financial SMS handling, remote command processing, device information reporting and telephony-related operations.

Although these capabilities create a potentially serious security risk, the available evidence does not establish successful execution, confirmed victim impact or the identity of the infrastructure operator.

The investigation is documented as a static-analysis and infrastructure-intelligence assessment, with its technical evidence, indicators, methodology and limitations maintained in the accompanying repository.

---

**Document classification:** Independent Security Research

**Investigation scope:** Android APK Static Analysis and C2 Infrastructure Intelligence

**Status:** Documented investigation phase