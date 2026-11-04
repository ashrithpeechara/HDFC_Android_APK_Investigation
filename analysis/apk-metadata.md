# APK Metadata Analysis

## 1. Overview

This document records the metadata and cryptographic identity of the Android application packages examined during the investigation.

Two APK artifacts were identified:

1. **Primary APK** — the externally supplied application package labelled `HDFC BANK LOAN SERVICE`.
2. **Embedded APK** — a secondary Android application recovered from an encrypted asset within the primary APK.

The metadata is documented separately to preserve artifact identity and avoid conflating the capabilities or behaviour of the two packages.

## 2. Primary APK Metadata

| Attribute | Value |
|---|---|
| Application label | `HDFC BANK LOAN SERVICE` |
| Package name | `com.sec.android.app.finance.kaxqj68` |
| Version name | `2.9.65` |
| Minimum SDK | `24` |
| Target SDK | `37` |
| Signing certificate subject | `CN=editor` |
| Signing algorithm/key | RSA 2048 |
| APK SHA-256 | `08cfe1f957d7539320eaaa97f1d6838182f5df57e6f875d00dc3060e432d35af` |
| Certificate SHA-256 | `6215f00baa4bf18bab5792fc796bfc5555917240f14f7c7e672d956888d75c96` |

### 2.1 Package identity observations

The application label references HDFC Bank and loan services. However, the package identifier is:

`com.sec.android.app.finance.kaxqj68`

The package name and displayed application label are metadata observations. Neither independently establishes that the application was developed, published, or authorised by HDFC Bank.

The signing certificate subject is `CN=editor`. This identifies the certificate's declared subject; it does not establish the identity of the developer or publisher.

### 2.2 Cryptographic identity

The SHA-256 digest of the primary APK is:

```text
08cfe1f957d7539320eaaa97f1d6838182f5df57e6f875d00dc3060e432d35af
```

This digest serves as the primary artifact's cryptographic identifier. It can be used to verify that subsequent copies of the APK match the examined sample.

The signing certificate fingerprint is:

```text
6215f00baa4bf18bab5792fc796bfc5555917240f14f7c7e672d956888d75c96
```

The APK hash and certificate fingerprint represent different things:

- **APK SHA-256:** identifies the complete APK file.
- **Certificate SHA-256:** identifies the signing certificate.

## 3. Embedded APK Metadata

### 3.1 Discovery and extraction

An additional APK artifact was recovered from the primary APK's assets.

The embedded file was named:

```text
rmtley9lr.db
```

The asset was identified as containing an APK protected using a repeating-XOR transformation. After decoding, the resulting artifact was recognised as a separate Android application package.

### 3.2 Embedded APK identity

| Attribute | Value |
|---|---|
| Original asset filename | `rmtley9lr.db` |
| Recovered artifact type | Android APK |
| Package name | `com.nxtwave.support` |
| Version name | `1.0` |
| Minimum SDK | `25` |
| Target SDK | `34` |
| Decoded APK SHA-256 | `13f93b8c70881f9414944fdc55811bfc627dbec966f023c664eb98782690cb4c` |
| Signing certificate | Same certificate as primary APK |

### 3.3 Archive integrity observations

The decoded APK was examined as a ZIP-based Android package.

| Check | Result |
|---|---|
| ZIP integrity test | Passed |
| Archive entries | 986 |
| Unusual path formatting | Observed |
| Absolute-style/backslash path entries | Observed |

The unusual path formatting is recorded as an archive observation. It is not sufficient, by itself, to establish path traversal or successful file extraction outside an intended directory.

### 3.4 Signing relationship

The embedded APK was found to use the same signing certificate as the primary APK.

This establishes a shared signing-certificate relationship between the two artifacts.

It does not independently establish:

- That both packages were built from the same source code.
- That the embedded APK was installed on a device.
- That the primary APK automatically executes or installs the embedded APK.
- That both packages have identical runtime behaviour.

Any execution or loading relationship requires separate code-level evidence.

## 4. Artifact Comparison

| Attribute | Primary APK | Embedded APK |
|---|---|---|
| Artifact origin | Supplied application package | Recovered from primary APK asset |
| Application label | HDFC BANK LOAN SERVICE | Not established here |
| Package name | `com.sec.android.app.finance.kaxqj68` | `com.nxtwave.support` |
| Version | `2.9.65` | `1.0` |
| Minimum SDK | 24 | 25 |
| Target SDK | 37 | 34 |
| SHA-256 | `08cfe1f957d7539320eaaa97f1d6838182f5df57e6f875d00dc3060e432d35af` | `13f93b8c70881f9414944fdc55811bfc627dbec966f023c664eb98782690cb4c` |
| Signing certificate | CN=editor | Same as primary APK |

## 5. Reproducible Verification Commands

The following commands can be used to independently verify the metadata when the corresponding artifacts are available.

### 5.1 Calculate SHA-256

```bash
sha256sum primary.apk
sha256sum embedded.apk
```

Compare the output against the recorded SHA-256 values above.

### 5.2 Inspect APK package metadata

Using Android SDK Build Tools:

```bash
aapt dump badging primary.apk
aapt dump badging embedded.apk
```

This can display package names, version information, SDK requirements, and application labels where available.

### 5.3 Inspect APK signing information

Using Android SDK Build Tools:

```bash
apksigner verify --verbose --print-certs primary.apk
apksigner verify --verbose --print-certs embedded.apk
```

Compare the certificate fingerprints with the recorded certificate SHA-256.

### 5.4 Test APK archive integrity

```bash
unzip -t primary.apk
unzip -t embedded.apk
```

A successful archive integrity test indicates that the ZIP entries can be read without the integrity errors detected by this test. It does not establish that the application is safe.

## 6. Forensic Interpretation

The metadata establishes two distinct APK artifacts with different package identifiers and version information.

The primary APK uses an application label referencing HDFC Bank, while its package identity and signing-certificate subject do not independently establish an official publisher relationship.

The embedded APK is a separate package recovered through decoding an asset from the primary APK. Both artifacts share the same signing certificate, which is a relevant relationship for subsequent static analysis.

These observations should be considered alongside the application's permissions, services, receivers, SMS functionality, Firebase configuration, network endpoints, and other code-derived capabilities documented in the repository.

## 7. Limitations

The following limitations apply to this metadata assessment:

1. Metadata alone cannot establish the application publisher's identity.
2. A shared signing certificate does not prove that the embedded APK is installed or executed.
3. Archive integrity does not establish application safety.
4. SDK values describe declared compatibility targets, not the actual Android environment in which the APK was executed.
5. No runtime execution or dynamic installation behaviour is established by this document.
6. The metadata does not establish whether any data was successfully transmitted to or stored by remote infrastructure.

## 8. Conclusion

The examination identified a primary APK labelled `HDFC BANK LOAN SERVICE` and a separately recovered embedded APK named `com.nxtwave.support`.

Both artifacts have recorded SHA-256 identities and share a signing certificate. The primary application's branding, package identity, embedded package, and signing information provide useful context for the broader static investigation.

These metadata findings are indicators for further assessment, not standalone proof of malicious execution, successful data exfiltration, or attribution to a particular individual or organisation.

---

**Document classification:** Static APK metadata assessment  
**Investigation type:** Android application security and forensic analysis  
**Execution status:** Static examination; dynamic analysis not performed