# Investigation Scripts

## 1. Purpose

This directory is intended to contain supporting scripts used during the examination, validation, and documentation of the Android APK investigation.

Scripts included in this directory should improve reproducibility by automating repeatable examination tasks and reducing manual errors.

The scripts are intended to support the investigation's static-analysis and infrastructure-documentation scope.

They must not be presented as proof of runtime behaviour unless their output is supported by independently collected evidence.

## 2. Current Status

The repository currently defines the scripts directory and its dependency manifest.

| Item | Status |
|---|---|
| Script documentation | Available |
| Python dependency manifest | Available |
| Analysis script inventory | Pending source-file verification |
| Automated test suite | Not established |
| Runtime-analysis automation | Outside investigation scope |

No specific executable script is claimed to be included until its source code and purpose are documented.

## 3. Recommended Directory Structure

As scripts are added, use a structure similar to:

```text
scripts/
├── README.md
├── requirements.txt
├── hashing/
│   └── sha256_manifest.py
├── metadata/
│   └── apk_metadata.py
├── validation/
│   ├── validate_iocs.py
│   └── validate_json.py
└── tests/
    └── README.md
```

This is a proposed structure, not a representation of files already present in the repository.

## 4. Recommended Script Categories

### 4.1 Evidence integrity

Potential responsibilities:

- Calculate SHA-256 hashes.
- Generate file-integrity manifests.
- Compare original and working-copy hashes.
- Validate evidence filenames and metadata.

### 4.2 APK metadata

Potential responsibilities:

- Extract APK package information.
- Record version and SDK attributes.
- Collect signing-certificate metadata.
- Generate structured metadata output.

### 4.3 IOC validation

Potential responsibilities:

- Validate JSON syntax.
- Check CSV structure.
- Identify missing indicator fields.
- Detect duplicate indicators.
- Validate SHA-256 formatting.

### 4.4 Report support

Potential responsibilities:

- Generate consistent evidence tables.
- Validate report references.
- Check that documented indicators match the IOC catalogue.
- Produce reproducible summary information.

These are suggested automation categories. They should only be described as implemented after the corresponding scripts are added and tested.

## 5. Environment Setup

Use a dedicated Python virtual environment when third-party packages are required.

### Linux / Kali Linux

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Windows

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install dependencies only after confirming that the scripts require them:

```bash
python -m pip install -r requirements.txt
```

## 6. Script Documentation Standard

Every executable script added to this repository should document:

| Field | Description |
|---|---|
| Script name | Filename |
| Purpose | What the script does |
| Input | Accepted files or arguments |
| Output | Generated files or terminal output |
| Dependencies | Required Python packages |
| Execution | Example command |
| Limitations | Known constraints |
| Validation | How its output was tested |

### Example documentation format

```markdown
## Script: example.py

**Purpose:** Describe the actual implemented functionality.

**Input:** Document accepted input files.

**Output:** Document generated output.

**Dependencies:** List confirmed dependencies.

**Execution:**

```bash
python example.py --help
```

**Limitations:** Document known limitations.
```

The example above is a documentation template, not an implemented script.

## 7. Evidence Safety Requirements

Scripts that handle investigative artifacts should follow these requirements:

1. Never modify original evidence by default.
2. Prefer read-only input handling.
3. Generate derived outputs in a separate directory.
4. Record SHA-256 hashes where integrity verification is relevant.
5. Avoid overwriting existing evidence or reports.
6. Do not print sensitive personal information unnecessarily.
7. Redact personal data before generating public reports.
8. Record errors instead of silently ignoring them.
9. Clearly distinguish generated output from original evidence.
10. Do not execute suspicious APKs as part of static-analysis scripts.

## 8. Reproducibility

For each script execution, document:

- Script version or Git commit.
- Python version.
- Operating system.
- Input artifact hash.
- Command-line arguments.
- Execution timestamp, where relevant.
- Output file names.
- Errors or warnings.

This information helps another analyst understand how a result was produced.

## 9. Scope Restrictions

The investigation documented in this repository is based on static APK examination and passive infrastructure intelligence.

Scripts should not silently introduce:

- APK execution.
- Live command-and-control interaction.
- Unauthorised endpoint requests.
- SMS transmission.
- USSD execution.
- Call-forwarding changes.
- Destructive device operations.

Any future dynamic-analysis tooling should be separately scoped, isolated, and documented.

## 10. Contribution Guidelines

Before adding a script:

1. Define its investigative purpose.
2. Identify its input and output.
3. Confirm that it does not alter original evidence.
4. Document dependencies.
5. Add usage instructions.
6. Test it with known inputs.
7. Record limitations.
8. Update this README.

**Principle:** Every automated result should be traceable, reproducible, and independently interpretable.