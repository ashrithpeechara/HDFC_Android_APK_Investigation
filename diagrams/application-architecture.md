# Android Application Architecture

## 1. Overview

This document illustrates the architecture identified during static examination of the primary Android APK.

The architecture represents the relationship between:

- Android application components.
- Background services and broadcast receivers.
- Firebase Cloud Messaging.
- SMS and telephony functionality.
- Remote HTTP endpoints.
- Embedded application artifacts.

The diagram is reconstructed from application configuration, Java decompilation, and Smali inspection. It is not a runtime-captured architecture.

## 2. High-Level Application Architecture

```mermaid
flowchart TB
    subgraph APK["Primary Android APK"]
        MA["MainActivity"]

        subgraph SERVICES["Application Services"]
            SS["SmsService"]
            SFS["SmsForwardService"]
            SSS["SmsSendService"]
            CS["CallService"]
            US["UssdService"]
            BS["BackgroundService"]
        end

        subgraph RECEIVERS["Broadcast Receivers"]
            SR["SmsReceiver"]
            BR["BootReceiver"]
        end

        subgraph FCM["Firebase Integration"]
            FMS["MyFirebaseMessagingService"]
            FT["FCM Token Registration"]
        end

        CFG["server.json"]
        NATIVE["libzwdwbxqi.so"]
        PREF["Shared Preferences"]
        EMB["Embedded APK Asset"]
    end

    MA --> SERVICES
    MA --> RECEIVERS
    MA --> FCM

    BR --> SFS
    SFS --> SR
    SR --> SS

    FMS --> SSS
    FMS --> SS
    FMS --> US

    CS --> CFG
    SS --> CFG
    SSS --> CFG
    US --> CFG
    BS --> CFG
    FT --> CFG

    SFS --> PREF
    NATIVE --> MA
    EMB --> APK
```

## 3. Component Responsibilities

| Component | Identified responsibility |
|---|---|
| `MainActivity` | Application entry point and service startup logic |
| `SmsService` | Financial SMS filtering and HTTP forwarding |
| `SmsForwardService` | SMS broadcast monitoring and forwarding workflow |
| `SmsReceiver` | Processes incoming SMS broadcast information |
| `SmsSendService` | Remote SMS transmission |
| `CallService` | Retrieves and processes call-forwarding configuration |
| `UssdService` | Handles USSD-related command workflow |
| `BackgroundService` | Device and SIM information reporting |
| `BootReceiver` | Starts SMS forwarding service after boot |
| `MyFirebaseMessagingService` | Processes incoming FCM command messages |
| `server.json` | Stores remote endpoint configuration |
| `libzwdwbxqi.so` | Native functionality including environment checks |
| Embedded APK asset | Contains a separately recovered APK |

## 4. Firebase Command Architecture

The application uses Firebase Cloud Messaging as a command-dispatch mechanism.

```mermaid
flowchart TD
    A["Firebase Cloud Messaging"] --> B["MyFirebaseMessagingService"]
    B --> C{"Received Command"}

    C -->|"ONLINE_CHECK"| D["Online State Update"]
    C -->|"PING"| D
    C -->|"SYNC_DEVICE"| E["Synchronisation State"]
    C -->|"SEND_SMS"| F["SmsSendService"]
    C -->|"GET_SMS"| G["SmsService"]
    C -->|"RUN_USSD"| H["UssdService"]

    I["FCM Token"] --> J["Token Registration Logic"]
    J --> K["save_token.php"]
```

The diagram represents command handlers identified in `MyFirebaseMessagingService.java`. It does not establish successful command delivery or execution.

## 5. SMS Processing Architecture

The application contains two distinct SMS forwarding paths and a separate remote SMS transmission service.

```mermaid
flowchart TD
    A["Incoming SMS"] --> B["SmsReceiver"]
    B --> C["SmsForwardService"]
    C --> D["SMS Processing Workflow"]
    D --> E["SmsService"]

    E --> F["Financial Message Filtering"]
    F --> G["sms_forward.php"]
    G --> H["Configured Remote Endpoint"]

    C --> I["Forwarding Configuration"]
    I --> J["sms_forward_number.php"]
    J --> K["forward_number and status"]
    K --> L["SmsManager"]
    L --> M["Configured Telephone Number"]

    N["FCM SEND_SMS Command"] --> O["SmsSendService"]
    O --> P["sms_send.php"]
    P --> Q["SmsManager Transmission"]
```

The two forwarding paths should not be conflated:

1. HTTP-based forwarding of filtered financial SMS messages.
2. SMS-body forwarding through a remotely configured telephone number.

`SmsSendService` implements a separate remote SMS transmission workflow.

## 6. Call-Forwarding and USSD Architecture

```mermaid
flowchart TD
    A["Remote Configuration"] --> B["CallService"]
    B --> C["call_forward_setting.php"]
    C --> D{"Call Status"}

    D -->|"on"| E["Enable Forwarding USSD"]
    D -->|"off"| F["Disable Forwarding USSD"]

    E --> G["TelephonyManager"]
    F --> G

    G --> H["Carrier USSD Processing"]
    H --> I["update_call_forward_url"]

    J["FCM RUN_USSD"] --> K["UssdService"]
    K --> L["USSD Request Workflow"]
    L --> M["update_ussd.php"]
```

The application contains these USSD-related code paths. Actual carrier acceptance and successful call redirection were not verified.

## 7. Remote Infrastructure Architecture

```mermaid
flowchart TB
    A["Android Application"]

    subgraph PRIMARY["Primary Configured Domain"]
        B["w60.kinginfo.online"]

        B --> C["background_service.php"]
        B --> D["sms_forward.php"]
        B --> E["sms_forward_number.php"]
        B --> F["sms_send.php"]
        B --> G["call_forward.php"]
        B --> H["call_forward_setting.php"]
        B --> I["save_token.php"]
        B --> J["permission.php"]
        B --> K["ussd_setting.php"]
        B --> L["update_ussd.php"]
        B --> M["web/api/check_online.php"]
        B --> N["app_upload.php"]
    end

    subgraph SECONDARY["Additional Configured Infrastructure"]
        O["host.kinginfo.online"]
        P["w60.mrkinginfoback.online"]
    end

    A --> B
    A --> O
    A --> P
    O --> Q["get.php"]
    P --> R["update_call_forward.php"]
```

The diagram represents configured endpoint relationships, not verified backend implementation or data flow during execution.

## 8. Native Library Architecture

The primary APK contains:

`libzwdwbxqi.so`

The library is a stripped ARM64 native library with JNI-related functions identified during static examination.

```mermaid
flowchart TD
    A["Android Application"] --> B["libzwdwbxqi.so"]

    B --> C["getSecretKey"]
    B --> D["nativeXorChunk"]
    B --> E["getTargetPackage"]
    B --> F["nativeScanEnv"]

    F --> G["Frida / Gadget Checks"]
    F --> H["Xposed / Substrate Checks"]
    F --> I["Thread Inspection"]
    F --> J["TracerPid Inspection"]
    F --> K["TCP Port Inspection"]
```

These checks are consistent with instrumentation and debugging-environment detection.

Their actual runtime effect was not tested.

## 9. Embedded APK Relationship

The primary APK contains an asset named:

`rmtley9lr.db`

After repeating-XOR decoding, the asset was recovered as an APK with package name:

`com.nxtwave.support`

```mermaid
flowchart TD
    A["Primary APK"] --> B["Assets Directory"]
    B --> C["rmtley9lr.db"]
    C --> D["Repeating-XOR Decoding"]
    D --> E["Recovered APK"]
    E --> F["com.nxtwave.support"]
    E --> G["SHA-256 Verification"]
    E --> H["APK Metadata Examination"]
```

Both APKs share the same signing certificate.

The architecture does not assert that the embedded APK is installed or executed by the primary application.

## 10. Architecture Assessment

The examined application contains multiple interconnected subsystems:

- SMS collection and forwarding.
- Remote SMS transmission.
- FCM command dispatch.
- Call-forwarding configuration.
- USSD operations.
- Device information reporting.
- Background service management.
- Native environment detection.
- Embedded APK storage.

The configuration-driven endpoint structure provides a common reference for the application's remote communication functionality.

## 11. Limitations

- Architecture reconstructed from static evidence.
- Dynamic execution was not performed.
- Actual runtime service interactions were not captured.
- FCM message delivery was not established.
- Backend implementation was not examined.
- Embedded APK execution linkage was not established.
- Successful SMS, USSD, or call-forwarding operations were not verified.

**Diagram classification:** Static architecture reconstruction  
**Primary artifact:** `com.sec.android.app.finance.kaxqj68`  
**Dynamic analysis:** Not performed