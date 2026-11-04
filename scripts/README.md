# Investigation Scripts

## 1. Overview

This directory contains Python utilities supporting the static examination and documentation of the Android APK investigation.

The scripts provide repeatable operations for:

- Evidence integrity verification.
- APK metadata and archive inspection.
- IOC validation.
- Offline DNS dataset analysis.
- Certificate-transparency dataset analysis.

The utilities are designed to support reproducibility and evidence handling. They do not execute the examined APK or establish runtime behaviour.

## 2. Script Inventory

| Script | Purpose | Input | Output |
|---|---|---|---|
| `sha256_manifest.py` | Calculate SHA-256 hashes | File or directory | CSV manifest |
| `apk_metadata.py` | Inspect APK metadata and archive structure | APK file | JSON report or terminal output |
| `validate_iocs.py` | Validate IOC JSON and CSV files | JSON, CSV or directory | Validation summary |
| `dns_analysis.py` | Summarise DNS observations | Structured JSON | JSON report or terminal output |
| `certificate_analysis.py` | Analyse certificate records and issuance intervals | Structured JSON | JSON report or terminal output |

## 3. Requirements

- Python 3.9 or later.
- Python standard library.
- Optional Android SDK command-line tools for extended APK metadata inspection.

### Optional Android tools

| Tool | Purpose |
|---|---|
| `aapt` / `aapt2` | APK package and SDK metadata |
| `apksigner` | Signing-certificate verification |

These tools are not Python dependencies.

No third-party Python packages are currently required.

## 4. Usage

Run the scripts from the repository root.

### 4.1 SHA-256 evidence manifest

Calculate hashes for a directory:

```bash
python scripts/sha256_manifest.py ./evidence \
    --output ./reports/evidence-manifest.csv
```

Calculate the hash of a single APK:

```bash
python scripts/sha256_manifest.py ./sample.apk \
    --output ./reports/apk-manifest.csv
```

The output includes:

- Relative file path.
- File size in bytes.
- SHA-256 digest.
- Processing status.
- Error information.
- UTC collection timestamp.

Existing output files are protected by default. Use `--force` only when intentionally replacing an existing manifest.

### 4.2 APK metadata inspection

Inspect an APK:

```bash
python scripts/apk_metadata.py ./sample.apk
```

Save the report:

```bash
python scripts/apk_metadata.py ./sample.apk \
    --output ./reports/apk-metadata.json
```

The script examines:

- APK SHA-256.
- ZIP archive integrity.
- Archive entry count.
- Uncompressed archive size.
- DEX files.
- Native libraries.
- Manifest presence.
- Signing-related archive files.
- Unusual archive entry paths.
- Optional package metadata.
- Optional signing verification.

The script does not install or execute the APK.

### 4.3 IOC validation

Validate the repository IOC directory:

```bash
python scripts/validate_iocs.py ./iocs/
```

Validate individual files:

```bash
python scripts/validate_iocs.py \
    ./iocs/hashes.json \
    ./iocs/domains.json \
    ./iocs/indicators.csv
```

Validation includes:

- JSON parsing.
- CSV parsing.
- Expected IOC CSV column checks.
- SHA-256 format checks where fields identify hashes.
- Empty indicator detection.
- Duplicate indicator warnings.

The validator performs local checks only. It does not query VirusTotal, MalwareBazaar, DNS services, or external threat-intelligence platforms.

### 4.4 Offline DNS analysis

Expected input example:

```json
{
    "records": [
        {
            "name": "example.com",
            "type": "A",
            "value": "192.0.2.10",
            "ttl": 300,
            "source": "previously-collected-dataset"
        },
        {
            "name": "example.com",
            "type": "AAAA",
            "value": "2001:db8::10"
        }
    ]
}
```

Run the analysis:

```bash
python scripts/dns_analysis.py ./evidence/dns-records.json
```

Save the summary:

```bash
python scripts/dns_analysis.py ./evidence/dns-records.json \
    --output ./reports/dns-summary.json
```

The script summarises record types, unique domains, and observed values.

It does not perform DNS lookups.

### 4.5 Certificate timeline analysis

Expected input example:

```json
{
    "certificates": [
        {
            "id": "certificate-001",
            "dns_names": [
                "example.com"
            ],
            "not_before": "2026-09-01T00:00:00Z",
            "not_after": "2026-11-30T00:00:00Z",
            "revoked": false,
            "pubkey_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "cert_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
    ]
}
```

Run the analysis:

```bash
python scripts/certificate_analysis.py \
    ./evidence/certificate-records.json
```

Save the output:

```bash
python scripts/certificate_analysis.py \
    ./evidence/certificate-records.json \
    --output ./reports/certificate-summary.json
```

The script calculates:

- Certificate record count.
- Unique certificate identifiers.
- Unique DNS names.
- Repeated DNS names.
- Public-key fingerprint diversity.
- Issuance intervals for repeated names.

It does not contact certificate-transparency services.

**Input compatibility note:** The example formats above describe the currently supported normalized JSON structures. Raw DNS or Cert Spotter exports may need preprocessing before they can be analysed correctly. The example datasets are illustrative and are not investigation evidence.

## 5. Output and Evidence Handling

The scripts should be used with preserved original evidence and separate working copies.

Recommended practices:

1. Preserve original APKs and evidence files.
2. Calculate hashes before examination.
3. Keep generated manifests and reports separate from source evidence.
4. Avoid overwriting existing evidence outputs.
5. Record tool versions and execution parameters.
6. Review errors and warnings rather than ignoring them.
7. Redact sensitive personal information before publishing outputs.

Generated reports are derived artifacts. They should not replace the original evidence or its acquisition records.

## 6. Investigation Scope

These scripts support the documented static-analysis and offline infrastructure-intelligence scope.

They do not perform:

- APK dynamic execution.
- Live C2 communication.
- Remote command execution.
- SMS transmission.
- USSD execution.
- Call-forwarding modification.
- Active infrastructure exploitation.
- Automated attribution of infrastructure operators.

## 7. Limitations

Automated output must be interpreted in context.

In particular:

- A matching SHA-256 hash supports file-integrity comparison but does not establish acquisition provenance.
- APK metadata does not establish application behaviour.
- Archive path anomalies do not independently prove exploitation or malicious intent.
- IOC syntax validation does not establish that an indicator is malicious.
- DNS records do not independently identify backend origin infrastructure.
- Certificate renewal intervals do not establish common ownership.
- Static configuration does not prove successful runtime communication.

## 8. Reproducibility

For reproducible results, document:

- Python version.
- Script filename.
- Input filename and SHA-256.
- Execution command.
- Output filename.
- Execution timestamp.
- Errors and warnings.

The generated output should be reviewed before being incorporated into the final investigation report.

## 9. Development Status

The scripts are repository-support utilities. Their presence does not imply that every utility was used during the original examination.

Before treating a script's output as an original investigation result, validate it against the corresponding source evidence and documented collection records.

**Investigation approach:** Static APK examination and offline infrastructure analysis.

**Execution policy:** No suspicious APK execution or active C2 interaction.