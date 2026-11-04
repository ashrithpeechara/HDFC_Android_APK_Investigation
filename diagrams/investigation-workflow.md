# Investigation Workflow

## Overview

This diagram represents the major stages followed during the Android APK and infrastructure investigation.

The workflow covers artifact identification, APK examination, embedded APK recovery, static code analysis, infrastructure intelligence, evidence documentation, and final reporting.

Dynamic analysis was outside the scope of the completed investigation.

## Investigation Process

```mermaid
flowchart TD
    A["APK Received"] --> B["Preserve Original Artifact"]
    B --> C["Calculate SHA-256"]
    C --> D["APK Metadata Examination"]

    D --> E["Manifest and Permission Analysis"]
    D --> F["Signing Certificate Analysis"]
    D --> G["Asset and Resource Examination"]

    G --> H{"Embedded APK Identified?"}
    H -->|Yes| I["Decode Embedded Asset"]
    I --> J["Validate Recovered APK"]
    J --> K["Record Secondary APK Metadata"]
    H -->|No| L["Continue Primary APK Analysis"]

    E --> M["Java and Smali Examination"]
    F --> M
    K --> M
    L --> M

    M --> N["SMS and Telephony Analysis"]
    M --> O["FCM Command Analysis"]
    M --> P["Persistence Analysis"]
    M --> Q["Native Anti-Analysis Examination"]

    N --> R["Extract Remote Configuration"]
    O --> R
    P --> R
    Q --> R

    R --> S["Passive Infrastructure Assessment"]
    S --> T["DNS and Domain Intelligence"]
    S --> U["TLS and Certificate Analysis"]
    S --> V["HTTP Endpoint Observations"]

    T --> W["Consolidate Evidence"]
    U --> W
    V --> W

    W --> X["Prepare Technical Findings"]
    X --> Y["Generate IOC Catalogue"]
    Y --> Z["Prepare Final Reports"]
    Z --> AA["Repository Documentation"]
```

## Investigation Phases

| Phase | Activities | Output |
|---|---|---|
| 01. Acquisition | Preserve APK and calculate hash | Artifact identity |
| 02. Metadata | Package, SDK and certificate examination | APK metadata |
| 03. Embedded artifact | Asset decoding and APK validation | Secondary APK |
| 04. Static analysis | Java, Smali, manifest and native library examination | Technical findings |
| 05. Infrastructure | Configuration, DNS, TLS and endpoint observations | Infrastructure intelligence |
| 06. Evidence | Record artifacts and handling information | Evidence register |
| 07. IOC extraction | Consolidate hashes, domains and identifiers | IOC catalogue |
| 08. Reporting | Document findings, confidence and limitations | Investigation reports |

## Scope Boundary

The completed workflow represents static examination and passive infrastructure assessment.

The following activities were not performed:

- Dynamic APK execution.
- Live application traffic capture.
- Victim-device acquisition.
- Backend database examination.
- Successful data-exfiltration verification.
- Infrastructure operator attribution.

## Important Evidence Principle

Every conclusion must be traceable to an artifact, code observation, or recorded infrastructure observation.

A code-derived capability must not be presented as confirmed runtime behaviour.

**Investigation status:** Static analysis and passive infrastructure assessment documented.