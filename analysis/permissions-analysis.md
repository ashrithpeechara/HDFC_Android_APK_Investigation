# Android Permissions Analysis

## 1. Overview

This document examines the permission-related security implications of the Android application labelled `HDFC BANK LOAN SERVICE`.

The analysis considers the application's documented code-level capabilities, including:

- SMS reception and processing.
- Financial SMS filtering and forwarding.
- Outbound SMS transmission.
- Call-forwarding configuration through USSD.
- Remote USSD command handling.
- Background service operation.
- Network communication with configured infrastructure.
- Firebase Cloud Messaging integration.

The objective is to establish the relationship between Android permission-controlled capabilities and the functionality identified during static analysis.

**Evidence limitation:** The complete permission list extracted from the primary APK's `AndroidManifest.xml` is not reproduced in the available investigation records. Therefore, this document does not claim that any particular permission was confirmed as declared or granted unless independently documented.

---

## 2. Permission Analysis: Important Distinctions

Android permission analysis requires separating three different questions.

| Layer | Question | What it establishes |
|---|---|---|
| Manifest declaration | Does the APK request a permission? | The application's declared permission requirements |
| Runtime/device grant | Was the permission granted on a particular device? | The permission state for that installation |
| Code-level usage | Does application code invoke functionality requiring that permission? | An implemented capability or attempted operation |

These layers must not be treated as interchangeable.

For example, the presence of SMS-related code does not prove that the application successfully accessed SMS messages. Similarly, a manifest declaration does not establish that the user granted the permission.

---

## 3. Identified Functional Capability Groups

The following table maps documented application functionality to the Android permission areas that should be examined.

**Note:** The permission names below are investigation targets based on the documented functionality. They are not a verified transcription of the APK manifest.

| Functional area | Permission or access area to verify | Relevant implementation |
|---|---|---|
| SMS reception | SMS-reception permissions and broadcast access | `SmsReceiver.java`, `SmsForwardService.java` |
| SMS reading | SMS-provider access permissions | `SmsService.java`, `F1/o.java` |
| SMS transmission | SMS-sending permission | `SmsSendService.java`, `A/n.java` |
| Telephony and SIM access | Phone-state and subscription-related permissions or APIs | `CallService.java`, `UssdService.java` |
| USSD execution | Telephony API access and device/carrier restrictions | `CallService.java`, `UssdService.java` |
| Network communication | Internet access | HTTP communication and configured endpoints |
| Background operation | Foreground-service and background-execution declarations | `BackgroundService.smali`, `SmsForwardService.java` |
| Boot persistence | Boot-completed broadcast access | `BootReceiver` |
| Firebase messaging | Firebase messaging service and associated manifest declarations | `MyFirebaseMessagingService.java` |

The exact permission names, protection levels, and manifest attributes must be confirmed from the original manifest before this mapping is treated as a verified permission inventory.

---

## 4. SMS-Related Capabilities

### 4.1 Incoming SMS processing

The investigation identified the following implementation components:

- `SmsReceiver.java`
- `SmsForwardService.java`
- `SmsService.java`

The documented implementation indicates that the application processes incoming SMS broadcasts, extracts message-related fields, and starts a service for further handling.

The examined code paths include:

- Originating address extraction.
- SMS message-body extraction.
- Timestamp extraction.
- Subscription and SIM-slot information.
- Forwarding-related service invocation.

**Security relevance:** Access to incoming SMS can expose authentication messages, financial notifications, transaction alerts, and other sensitive communications.

### 4.2 Historical SMS processing

`F1/o.java` contains historical SMS processing logic.

The available analysis records indicate that it:

- Queries the SMS inbox provider.
- Uses a 30-day time window.
- Applies financial-message filtering through `SmsService.b`.
- Processes matching messages for forwarding.
- Splits messages into 160-character chunks.

This is a code-derived capability. The investigation does not establish that the application successfully accessed or transmitted a victim's historical SMS messages.

### 4.3 SMS transmission

`SmsSendService.java` contains functionality for sending SMS messages through Android's `SmsManager`.

The documented implementation includes:

- SIM/subscription selection.
- Single-part and multipart SMS handling.
- SMS-sent and SMS-delivered broadcast handling.
- Retry handling, with up to three retries documented in the examined implementation.

The presence of this functionality does not prove that a remote command was received or that an SMS was successfully transmitted.

---

## 5. Telephony and USSD-Related Capabilities

### 5.1 Call-forwarding configuration

`CallService.java` retrieves call-forwarding configuration from a remote endpoint.

The documented implementation processes:

- `call_status`
- `call_number`
- `sim_slot`

It constructs the following USSD strings:

```text
**21*<number>#
##21#
```

The first string is used for call-forwarding activation, while the second is used for deactivation.

The service invokes Android telephony APIs through `TelephonyManager.createForSubscriptionId(...).sendUssdRequest(...)`.

**Security relevance:** If successfully executed on a supported device and network, call-forwarding manipulation could redirect incoming calls to another number.

**Limitation:** Static code analysis does not establish successful execution, carrier acceptance, or a change in the device's actual call-forwarding state.

### 5.2 Remote USSD handling

`MyFirebaseMessagingService.java` contains a command-dispatch path for the `RUN_USSD` action.

The documented command fields include:

- `request_id`
- `ussd_code`
- `sim_slot`

The command path starts `UssdService.java`, which prepares a status report containing:

- `device_id`
- `command_id`
- `ussd_code`
- `sim_slot`
- `status`
- `response`
- `error`

This demonstrates a code-level remote USSD handling capability. It does not establish that a command was received or executed on a real device.

---

## 6. Background Execution and Persistence

The investigation identified background execution components:

| Component | Documented role |
|---|---|
| `BackgroundService.smali` | Device-information reporting to configured infrastructure |
| `SmsForwardService.java` | SMS-related background service |
| `BootReceiver` | Starts the SMS forwarding service during boot-related handling |
| `MyFirebaseMessagingService.java` | Processes Firebase message actions |

The application also contains code that checks connectivity and communicates with configured remote endpoints.

These components warrant examination of:

- Foreground-service declarations.
- Background execution requirements.
- Boot-completed receiver declarations.
- Service export status.
- Broadcast receiver export status.
- Required permissions and component-level access controls.

The existence of a boot receiver does not, by itself, prove that persistence was successfully established on a particular device.

---

## 7. Network and Firebase Access

The documented application functionality includes HTTP communication with configured infrastructure and Firebase Cloud Messaging integration.

Relevant implementation components include:

- `MyFirebaseMessagingService.java`
- `BackgroundService.smali`
- `A/n.java`
- `SmsService.java`
- `CallService.java`
- `UssdService.java`

The application contains code paths for:

1. Registering an FCM token with a configured endpoint.
2. Reporting device information.
3. Checking connectivity and online state.
4. Processing remote command actions.
5. Communicating SMS, call-forwarding, and USSD-related information.

The exact manifest declarations for Internet access, Firebase services, and any associated component permissions must be verified directly against the APK manifest.

---

## 8. Manifest Verification Procedure

The following commands can be used to generate a verified permission inventory from the primary APK.

These are reproducibility instructions; they should not be interpreted as proof that the commands were executed during the original investigation.

### 8.1 Decode the APK

```bash
apktool d -f primary.apk -o primary_decoded
```

### 8.2 Locate permission declarations

```bash
grep -nE 'uses-permission|permission-group|permission ' \
  primary_decoded/AndroidManifest.xml
```

### 8.3 Inspect the manifest

```bash
less primary_decoded/AndroidManifest.xml
```

Pay particular attention to:

- `<uses-permission>`
- `<uses-permission-sdk-23>`
- `<permission>`
- `<service>`
- `<receiver>`
- `android:exported`
- `android:permission`
- `android:foregroundServiceType`

### 8.4 Generate a package summary

```bash
aapt dump permissions primary.apk
```

This command provides a useful permission summary from the APK.

### 8.5 Inspect component declarations

```bash
aapt dump xmltree primary.apk AndroidManifest.xml
```

Use this output to examine manifest components and their associated attributes.

---

## 9. Permission Inventory: Verification Status

The following table tracks what must be confirmed before publishing a definitive manifest permission inventory.

| Verification item | Current status |
|---|---|
| Complete primary APK permission list | Not available in current investigation notes |
| Complete secondary APK permission list | Not available in current investigation notes |
| SMS-related manifest declarations | Requires manifest verification |
| Telephony-related manifest declarations | Requires manifest verification |
| Internet permission declaration | Requires manifest verification |
| Foreground-service declarations | Requires manifest verification |
| Boot receiver declaration and attributes | Component identified; manifest attributes require verification |
| Firebase service declaration | Requires manifest verification |
| Runtime permission grants | Not established |
| Permission usage on an actual device | Not established |

Do not mark an item as verified until its manifest entry or device-level evidence has been examined.

---

## 10. Security Assessment

The code-level capabilities identified during static analysis have meaningful security implications.

| Capability | Potential security impact | Evidence strength |
|---|---|---|
| Incoming SMS processing | Exposure of private and financial messages | Code-derived |
| Historical SMS querying | Access to historical financial notifications | Code-derived |
| HTTP SMS forwarding | Potential transmission of message contents to remote infrastructure | Code-derived |
| Outbound SMS handling | Potential unauthorized SMS transmission | Code-derived |
| Call-forwarding manipulation | Potential redirection of incoming calls | Code-derived |
| Remote USSD handling | Potential execution of remotely supplied USSD requests | Code-derived |
| Background services | Continued operation outside the foreground UI | Code-derived |
| Firebase command dispatch | Remote action handling through FCM | Code-derived |

These capabilities warrant further security scrutiny, particularly when considered together with the application's financial-message filtering and configured remote infrastructure.

However, this table describes potential capability and impact. It does not establish successful exploitation, device compromise, or victim impact.

---

## 11. Limitations

1. The complete manifest permission inventory is not reproduced in the available investigation records.
2. Runtime permission grants were not collected.
3. No victim-device permission state was acquired.
4. Static analysis does not prove that a permission-controlled operation succeeded.
5. Android version, target SDK, device manufacturer, and carrier restrictions can affect permission and API behavior.
6. Dynamic analysis was not performed.
7. The relationship between declared permissions and every individual code path requires direct manifest and call-path verification.

---

## 12. Conclusion

The examined application contains code-level functionality associated with SMS processing, SMS transmission, telephony operations, USSD handling, background execution, network communication, and Firebase command dispatch.

These capabilities create potential privacy, financial, and communications-security risks if the application obtains the necessary access and the relevant operations execute successfully.

A definitive permission assessment requires the original `AndroidManifest.xml` and, for device-level conclusions, runtime permission-state evidence.

The next stage of analysis should correlate verified manifest declarations with the implementation paths documented in the SMS, call-forwarding, USSD, and Firebase analysis documents.

---

*Analysis type: Static permission and capability assessment.*

*Manifest verification status: Pending complete permission inventory.*

*Runtime permission status: Not established.*

*Dynamic analysis: Not performed.*