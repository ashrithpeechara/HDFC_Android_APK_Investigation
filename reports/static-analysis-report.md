# Android APK Static Analysis Report

## 1. Report Information

| Field | Details |
|---|---|
| Report title | Android APK Static Analysis Report |
| Application label | HDFC BANK LOAN SERVICE |
| Primary package | `com.sec.android.app.finance.kaxqj68` |
| Application version | `2.9.65` |
| Analysis type | Static APK analysis |
| Supporting analysis | Smali inspection, embedded APK extraction, configuration analysis |
| Dynamic analysis | Not performed |
| Report classification | Technical security investigation |
| Assessment status | Static findings documented |

## 2. Executive Summary

A static security examination was conducted on an Android application package displaying the label **HDFC BANK LOAN SERVICE**.

The investigation identified several security-relevant capabilities within the application's code and configuration, including:

- Collection and HTTP forwarding of financial and banking-related SMS messages.
- A separate SMS forwarding mechanism controlled through remote configuration.
- Remote SMS transmission functionality.
- Firebase Cloud Messaging (FCM)-based command dispatch.
- Remote call-forwarding configuration through USSD requests.
- Remote USSD command execution and status reporting.
- Device information collection and communication with configured remote endpoints.
- Native anti-analysis checks targeting instrumentation and debugging environments.
- An additional APK recovered from an encrypted asset within the primary package.

The application contains multiple configured endpoints under the `kinginfo.online` infrastructure, with an additional endpoint under `mrkinginfoback.online`.

The findings indicate a potentially significant risk to device communications, SMS privacy, and telephony functionality if the relevant code paths are executed with the necessary permissions and environmental support.

However, this investigation was limited to static analysis and passive infrastructure observations. It did not establish successful installation, runtime execution, actual SMS exfiltration, successful call forwarding, successful USSD operations, or server-side storage of transmitted information.

**Overall assessment:** Highly suspicious Android application with code-derived capabilities associated with remote device control and potentially unauthorised access to sensitive communications. Its claimed HDFC Bank affiliation has not been independently verified.

## 3. Scope and Objectives

The objectives of this investigation were:

1. Establish the cryptographic identity and metadata of the supplied APK.
2. Identify application components, permissions, services, and receivers relevant to security.
3. Examine SMS collection, filtering, forwarding, and transmission functionality.
4. Identify FCM-based remote command handling.
5. Examine call-forwarding and USSD functionality.
6. Identify device information collection and persistence mechanisms.
7. Examine native anti-analysis functionality.
8. Extract and identify additional APK artifacts.
9. Document configured remote infrastructure and associated indicators.
10. Produce a reproducible, evidence-oriented technical assessment.

### 3.1 Scope limitations

The investigation covered static APK examination, code inspection, configuration extraction, and passive infrastructure intelligence.

The following activities were not performed:

- Execution of the APK on a victim device.
- Controlled dynamic analysis.
- Live interception of application traffic during execution.
- Confirmation of successful remote command delivery.
- Verification of server-side data storage.
- Attribution of the application to a specific individual or organisation.

## 4. Examined Artifacts

### 4.1 Primary APK

| Attribute | Value |
|---|---|
| Application label | `HDFC BANK LOAN SERVICE` |
| Package name | `com.sec.android.app.finance.kaxqj68` |
| Version | `2.9.65` |
| Minimum SDK | 24 |
| Target SDK | 37 |
| Signing subject | `CN=editor` |
| Signing key | RSA 2048 |
| SHA-256 | `08cfe1f957d7539320eaaa97f1d6838182f5df57e6f875d00dc3060e432d35af` |
| Certificate SHA-256 | `6215f00baa4bf18bab5792fc796bfc5555917240f14f7c7e672d956888d75c96` |

### 4.2 Embedded APK

An additional APK was recovered from the primary application's asset named `rmtley9lr.db`. The asset used a repeating-XOR transformation.

| Attribute | Value |
|---|---|
| Original asset | `rmtley9lr.db` |
| Recovered package | `com.nxtwave.support` |
| Version | `1.0` |
| Minimum SDK | 25 |
| Target SDK | 34 |
| SHA-256 | `13f93b8c70881f9414944fdc55811bfc627dbec966f023c664eb98782690cb4c` |
| Signing certificate | Same as primary APK |

The decoded package passed ZIP integrity testing and contained 986 entries. Unusual absolute-style and backslash path formatting was observed. This alone does not establish path traversal.

The shared signing certificate is a relationship between the two artifacts, but it does not prove that the secondary APK is installed or executed by the primary application.

## 5. Technical Findings

### 5.1 Financial SMS collection and HTTP forwarding

<badge color="danger">High concern</badge>

The investigation identified SMS filtering and forwarding functionality in `SmsService.java`.

The filtering logic includes patterns associated with:

- Banking institutions.
- Account and balance notifications.
- Transaction and credit notifications.
- UPI and payment-related messages.
- Wallet and payment applications.

The method `b(String)` performs financial-message filtering.

The method `c(...)` retrieves the configured `sms_forward_url` from `server.json` and constructs an HTTP POST request containing fields including:

| Field | Description |
|---|---|
| `device_id` | Device identifier |
| `sender` | SMS sender |
| `user_number` | User number field |
| `message` | SMS message body |
| `timestamp` | Message timestamp |
| `type` | Message category |
| `part_number` | Multipart message part |
| `total_parts` | Total multipart message parts |

The request is transmitted using URL-encoded form data.

**Security significance:** If executed with the required permissions and connectivity, this functionality could transmit sensitive banking and financial SMS content to a configured remote endpoint.

**Evidence boundary:** The code demonstrates request construction and transmission logic. It does not establish that a remote server successfully received or stored any SMS.

### 5.2 Separate SMS forwarding mechanism

<badge color="danger">High concern</badge>

A second SMS forwarding path was identified.

The relevant components include:

- `SmsForwardService.java`
- `SmsReceiver.java`
- `A/n.java`

The service registers for the Android SMS-received broadcast. The receiver extracts message information and passes it into the service workflow.

The configuration logic in `A/n.java` periodically retrieves forwarding settings from the configured `sms_forward_number` endpoint.

The response contains fields named:

- `forward_number`
- `status`

When the returned status is `on`, the code uses Android's `SmsManager` functionality to forward the SMS body to the configured number.

When connectivity is unavailable, previously stored preferences may be used.

This mechanism is distinct from the HTTP-based financial SMS forwarding functionality described in Section 5.1.

**Security significance:** The application contains a separate mechanism capable of forwarding received SMS message content to a remotely configured telephone number.

**Evidence boundary:** The code establishes the forwarding capability and configuration logic. Successful SMS delivery was not demonstrated.

### 5.3 Remote SMS transmission

<badge color="danger">High concern</badge>

`SmsSendService.java` implements functionality for processing remote SMS transmission jobs.

The identified functionality includes:

- Retrieving the configured `sms_send_url`.
- Obtaining the Android device identifier.
- Selecting a SIM or subscription.
- Sending messages using `SmsManager`.
- Supporting multipart SMS transmission.
- Registering SMS-sent and SMS-delivered broadcast receivers.
- Implementing retry handling, with up to three retries.

The retry delays observed in the implementation are approximately 2, 4, and 6 seconds.

The FCM command handler can start this service through the `SEND_SMS` action.

**Security significance:** The application contains code capable of sending SMS messages under remote command control.

**Evidence boundary:** The presence of transmission and retry logic does not prove that a remote command was received or that any SMS was successfully sent.

### 5.4 Firebase Cloud Messaging command handling

<badge color="danger">High concern</badge>

`MyFirebaseMessagingService.java` implements a command-dispatch mechanism based on Firebase Cloud Messaging.

The following command identifiers were identified:

| Command | Code-derived function |
|---|---|
| `ONLINE_CHECK` | Updates online state |
| `SYNC_DEVICE` | Updates device synchronisation state |
| `PING` | Updates online state |
| `SEND_SMS` | Starts `SmsSendService` |
| `GET_SMS` | Starts `SmsService` with `fetch_latest_sms=true` |
| `RUN_USSD` | Starts `UssdService` with request parameters |

The `RUN_USSD` command processes values including:

- `request_id`
- `ussd_code`
- `sim_slot`

The service also contains logic to initiate FCM token registration.

**Security significance:** FCM is used as a remote command-dispatch mechanism for several sensitive device operations.

**Evidence boundary:** Static code establishes command-handling functionality. It does not establish that an operator sent commands, that Firebase delivered them, or that the device executed them successfully.

### 5.5 Device information collection

<badge color="warning">Medium–high concern</badge>

The investigation examined `BackgroundService.smali` because the corresponding JADX source was incomplete.

The Smali implementation constructs an HTTP POST request to the configured `background_service.php` endpoint.

The request includes fields such as:

- `device_name`
- `device_model`
- `device_id`
- `sim1_carrier`
- `sim2_carrier`
- `sim1_number`
- `sim2_number`
- `created_at`
- `last_seen`
- `status`
- `battery`

The request uses `HttpURLConnection` and URL-encoded form data.

**Security significance:** The application contains functionality for reporting device and SIM-related information to remote infrastructure.

**Evidence boundary:** The request construction and transmission code were identified. Successful server-side receipt or storage was not established.

### 5.6 Call-forwarding manipulation

<badge color="danger">High concern</badge>

`CallService.java` contains functionality for retrieving remote call-forwarding configuration.

The service periodically checks the configured `call_setting_url` endpoint and processes fields including:

- `call_status`
- `call_number`
- `sim_slot`

The identified operations include:

| Remote state | USSD operation |
|---|---|
| `on` | `**21*<number>#` |
| `off` | `##21#` |

The implementation uses `TelephonyManager.createForSubscriptionId(...).sendUssdRequest(...)` for subscription-specific USSD execution.

The service also reports operation status through the configured `update_call_forward_url` endpoint.

**Security significance:** The code contains functionality intended to manipulate call-forwarding settings through USSD.

**Evidence boundary:** Actual carrier acceptance, call-forwarding activation, and successful redirection were not verified.

### 5.7 USSD command execution

<badge color="danger">High concern</badge>

`MyFirebaseMessagingService.java` can dispatch the `RUN_USSD` command to `UssdService.java`.

The service processes command-related parameters and uses the configured `update_ussd_url` endpoint to report operation information.

The report fields include:

- `device_id`
- `command_id`
- `ussd_code`
- `sim_slot`
- `status`
- `response`
- `error`

The implementation contains callback logic for reporting completed or failed operations based on response information.

**Security significance:** The application contains a remote USSD execution workflow. Depending on the command and carrier support, USSD operations may interact with sensitive telephony services.

**Evidence boundary:** The exact successful execution of a remote USSD command was not established. The `UssdService.onStartCommand()` method was not fully recovered through JADX, so the precise invocation path requires additional Smali verification.

### 5.8 Persistence and service execution

<badge color="warning">Medium–high concern</badge>

The investigation identified service-management and startup-related components.

Relevant observations include:

- `BootReceiver` starts `SmsForwardService`.
- `MainActivity` starts SMS-related services after permission handling.
- `SmsForwardService` registers for SMS-received broadcasts.
- Forwarding configuration and status are stored in shared preferences.

These components indicate mechanisms intended to maintain or restore application functionality.

**Security significance:** Startup-triggered service activation can allow sensitive functionality to resume after device boot, depending on Android restrictions, permissions, and execution conditions.

**Evidence boundary:** Static code indicates intended startup and service behaviour. Successful persistence across device reboots was not tested.

### 5.9 Native anti-analysis functionality

<badge color="warning">Medium–high concern</badge>

The primary APK includes a native library:

`libzwdwbxqi.so`

The library is stripped ARM64 and exposes JNI-related functions including:

- `getSecretKey`
- `nativeXorChunk`
- `getTargetPackage`
- `nativeScanEnv`

The `nativeScanEnv` implementation contains checks associated with:

- Frida-related process mappings.
- Xposed and Substrate references.
- Gadget-related strings.
- Frida or Gum-related threads.
- `/proc/net/tcp` and `/proc/net/tcp6` entries associated with ports `27042` and `27043`.
- The process `TracerPid` value.

**Security significance:** These checks are consistent with attempts to detect instrumentation, hooking, or debugging environments.

**Evidence boundary:** The presence of anti-analysis checks does not independently prove malicious intent. Their runtime effect was not tested.

## 6. Configured Remote Infrastructure

The primary APK contains a `server.json` configuration file with several remote service endpoints.

| Function | Configured endpoint |
|---|---|
| Background service | `https://w60.kinginfo.online/background_service.php` |
| SMS forwarding | `https://w60.kinginfo.online/sms_forward.php` |
| SMS forwarding number configuration | `https://w60.kinginfo.online/sms_forward_number.php` |
| Call forwarding | `https://w60.kinginfo.online/call_forward.php` |
| Call-forwarding settings | `https://w60.kinginfo.online/call_forward_setting.php` |
| Remote SMS sending | `https://w60.kinginfo.online/sms_send.php` |
| Application upload | `https://w60.kinginfo.online/app_upload.php` |
| Permission configuration | `https://w60.kinginfo.online/permission.php` |
| FCM token registration | `https://w60.kinginfo.online/save_token.php` |
| Online status | `https://w60.kinginfo.online/web/api/check_online.php` |
| USSD settings | `https://w60.kinginfo.online/ussd_setting.php` |
| USSD status reporting | `https://w60.kinginfo.online/update_ussd.php` |
| Call-forwarding status update | `https://w60.mrkinginfoback.online/update_call_forward.php` |
| Web configuration | `https://host.kinginfo.online/get.php` |

### 6.1 Firebase configuration

The recovered Firebase configuration includes:

| Attribute | Value |
|---|---|
| Project ID | `fcmtoken-af5a6` |
| Sender ID | `705898731` |
| App ID | `1:705898731153:web:130e5565c49b143bfb9130` |
| API key | Redacted |

The Firebase configuration is consistent with the application's FCM command-handling implementation.

### 6.2 Infrastructure observations

The investigation recorded the following:

- `kinginfo.online` is configured as the primary application service domain.
- `host.kinginfo.online` provides a separate configuration endpoint.
- The call-forwarding update endpoint uses `mrkinginfoback.online`.
- The observed DNS responses for the primary subdomains included Cloudflare edge addresses.
- Certificate transparency observations identified multiple certificate records associated with numbered `w` subdomains.
- The observed endpoint audit returned HTTP 200 responses for 12 endpoints.
- The `w60.mrkinginfoback.online` endpoint returned a DNS resolution error during the audit.

Cloudflare edge IP addresses must not be interpreted as verified origin-server addresses. HTTP 200 responses establish that an HTTP response was returned, not that the associated application operation succeeded.

Detailed infrastructure findings are documented separately in the `infrastructure/` directory.

## 7. Risk Assessment

The following ratings represent the potential security impact of the identified code-derived capabilities. They are not a measurement of confirmed victim impact.

| Finding | Potential severity | Confidence in static finding |
|---|---|---|
| Financial SMS filtering and HTTP forwarding | High | High |
| Separate SMS forwarding mechanism | High | High |
| Remote SMS transmission | High | High |
| FCM command dispatch | High | High |
| Device and SIM information reporting | Medium–High | High |
| Call-forwarding manipulation | High | High |
| Remote USSD workflow | High | Medium–High |
| Boot-triggered service functionality | Medium–High | High |
| Native anti-analysis checks | Medium–High | High |
| Embedded secondary APK | Requires separate assessment | High |

### 7.1 Risk interpretation

The highest-risk capabilities concern sensitive SMS processing, remote SMS transmission, and telephony manipulation.

If the relevant code paths are activated with the required permissions and supported device/carrier conditions, they could affect the confidentiality of financial communications and the integrity of telephony settings.

The investigation does not establish that any of these potential impacts occurred on a real device.

## 8. Evidence and Confidence Model

This report distinguishes between four evidence categories.

| Category | Meaning | Example from investigation |
|---|---|---|
| Direct artifact observation | Information recovered directly from an APK or configuration file | Package name, SHA-256, Firebase project ID |
| Code-derived capability | Functionality represented in source or Smali | SMS forwarding request construction |
| Infrastructure observation | Response or DNS/TLS information collected during passive assessment | HTTP 200 response, DNS resolution |
| Runtime-confirmed behaviour | Behaviour reproduced during controlled execution | Not established in this investigation |

Confidence refers to confidence in the documented observation, not proof of real-world impact.

The absence of dynamic analysis is an important limitation when interpreting the application's operational behaviour.

## 9. Recommended Defensive Actions

For organisations or individuals who receive this application unexpectedly:

1. Do not install or execute the APK on a personal or operational device.
2. Preserve the original APK and record its SHA-256 hash.
3. Preserve relevant distribution URLs, messages, timestamps, and submission context.
4. If the APK has already been installed, assess the device using an appropriate incident-response process.
5. Review SMS, call-forwarding, USSD, application-permission, and device-administration settings where applicable.
6. Review financial accounts and contact the relevant financial institution through independently verified official channels if compromise is suspected.
7. Preserve logs and device evidence before making changes that could destroy forensic artifacts.
8. Submit the sample and findings to the relevant organisation or authorised incident-response authority.

Do not attempt to contact or interact with infrastructure or telephone numbers identified in the investigation unless explicitly authorised and covered by an approved test plan.

## 10. Investigation Limitations

The following limitations must be considered when interpreting this report:

- Dynamic analysis was not performed.
- No controlled Android execution environment was used to validate runtime behaviour.
- No victim-device acquisition was performed as part of this investigation.
- Successful SMS transmission or exfiltration was not established.
- Successful call forwarding or USSD execution was not established.
- FCM command delivery was not established.
- Server-side receipt or storage of transmitted information was not established.
- The identity of the application developer or infrastructure operator was not established.
- The application's claimed association with HDFC Bank has not been independently confirmed.

## 11. Conclusion

The static examination identified a highly suspicious Android application displaying the label `HDFC BANK LOAN SERVICE`.

The APK contains multiple code-derived capabilities involving financial SMS filtering, SMS forwarding, remote SMS transmission, FCM command dispatch, device information reporting, call-forwarding manipulation, USSD operations, startup-related service functionality, and native anti-analysis checks.

An additional APK was recovered from an encrypted asset within the primary package. Both APKs share a signing certificate but have distinct package identities.

The configured remote infrastructure and observed endpoint responses provide additional context for the investigation. However, these observations do not establish successful communication, data storage, victim impact, or operator attribution.

The evidence supports classifying the application as **highly suspicious and potentially capable of unauthorised access to sensitive communications and telephony operations**.

Further conclusions about actual compromise or attribution would require additional independently collected evidence.

---

## 12. Related Repository Documentation

| Document | Purpose |
|---|---|
| `analysis/apk-metadata.md` | APK identity and cryptographic metadata |
| `analysis/permissions-analysis.md` | Permission assessment |
| `analysis/sms-analysis.md` | SMS collection and forwarding |
| `analysis/fcm-analysis.md` | FCM command handling |
| `analysis/call-forwarding-analysis.md` | Call-forwarding functionality |
| `analysis/ussd-analysis.md` | USSD execution |
| `analysis/persistence-analysis.md` | Startup and service persistence |
| `analysis/anti-analysis.md` | Native anti-analysis checks |
| `infrastructure/firebase-analysis.md` | Firebase configuration |
| `infrastructure/endpoint-observations.md` | Endpoint audit observations |
| `infrastructure/dns-analysis.md` | DNS observations |
| `infrastructure/tls-analysis.md` | TLS and certificate intelligence |
| `evidence/evidence-register.md` | Evidence inventory |
| `evidence/chain-of-custody.md` | Evidence handling record |

**Report status:** Static analysis report  
**Dynamic analysis status:** Not performed  
**Attribution status:** Undetermined  
**Victim impact status:** Not established