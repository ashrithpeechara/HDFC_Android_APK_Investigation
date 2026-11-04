#!/usr/bin/env python3
"""
APK Metadata and Structure Inspector

Collects static APK metadata, archive structure, DEX information,
native library information, and optional Android signing information.

The APK is opened as a ZIP archive and is never installed or executed.

External tools:
    - aapt or aapt2 (optional): package and SDK metadata
    - apksigner (optional): signing certificate verification

Python dependencies:
    Standard library only.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

from datetime import datetime, timezone
from pathlib import Path


CHUNK_SIZE = 1024 * 1024


def calculate_sha256(path):
    """Calculate SHA-256 using streaming reads."""
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            digest.update(chunk)

    return digest.hexdigest()


def find_android_tool(names):
    """Find the first available Android command-line tool."""
    for name in names:
        executable = shutil.which(name)
        if executable:
            return executable

    return None


def run_tool(command, timeout=30):
    """Execute a local metadata tool without invoking a shell."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        return {
            "available": True,
            "return_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    except subprocess.TimeoutExpired:
        return {
            "available": True,
            "error": "Command timed out",
        }

    except OSError as exc:
        return {
            "available": False,
            "error": str(exc),
        }


def inspect_archive(apk_path):
    """Inspect APK ZIP entries without extracting them."""
    result = {
        "zip_integrity": "UNKNOWN",
        "entry_count": 0,
        "total_uncompressed_size": 0,
        "dex_files": [],
        "native_libraries": [],
        "manifest_present": False,
        "certificate_files": [],
        "suspicious_path_entries": [],
        "archive_errors": [],
    }

    with zipfile.ZipFile(apk_path, "r") as archive:
        bad_member = archive.testzip()

        result["zip_integrity"] = (
            "PASS" if bad_member is None else "FAIL"
        )

        if bad_member:
            result["archive_errors"].append(
                f"Corrupt archive member: {bad_member}"
            )

        for entry in archive.infolist():
            name = entry.filename
            normalized = name.replace("\\", "/")

            result["entry_count"] += 1
            result["total_uncompressed_size"] += entry.file_size

            if normalized == "AndroidManifest.xml":
                result["manifest_present"] = True

            if normalized.endswith(".dex"):
                result["dex_files"].append({
                    "name": name,
                    "size_bytes": entry.file_size,
                })

            if normalized.startswith("lib/") and normalized.endswith(".so"):
                result["native_libraries"].append({
                    "name": name,
                    "size_bytes": entry.file_size,
                })

            if normalized.startswith("META-INF/") and (
                normalized.endswith(".RSA")
                or normalized.endswith(".DSA")
                or normalized.endswith(".EC")
                or normalized.endswith(".SF")
            ):
                result["certificate_files"].append(name)

            path_parts = normalized.split("/")

            if (
                normalized.startswith("/")
                or "\\" in name
                or ".." in path_parts
            ):
                result["suspicious_path_entries"].append(name)

    return result


def inspect_aapt(apk_path):
    """Collect package information using aapt or aapt2."""
    tool = find_android_tool(["aapt", "aapt2"])

    if not tool:
        return {
            "available": False,
            "error": "Neither aapt nor aapt2 was found in PATH.",
        }

    return run_tool([tool, "dump", "badging", str(apk_path)])


def inspect_signature(apk_path):
    """Collect signing information using apksigner, if available."""
    tool = find_android_tool(["apksigner"])

    if not tool:
        return {
            "available": False,
            "error": "apksigner was not found in PATH.",
        }

    return run_tool([
        tool,
        "verify",
        "--verbose",
        "--print-certs",
        str(apk_path),
    ])


def inspect_apk(apk_path):
    """Build the complete static metadata report."""
    if not zipfile.is_zipfile(apk_path):
        raise ValueError("Input is not a valid ZIP/APK archive.")

    archive_info = inspect_archive(apk_path)

    report = {
        "tool": "APK Metadata and Structure Inspector",
        "analysis_type": "Static",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact": {
            "filename": apk_path.name,
            "size_bytes": apk_path.stat().st_size,
            "sha256": calculate_sha256(apk_path),
        },
        "archive": archive_info,
        "android_metadata": inspect_aapt(apk_path),
        "signature_verification": inspect_signature(apk_path),
        "limitations": [
            "APK was not installed or executed.",
            "Binary AndroidManifest.xml is not decoded by this script.",
            "Package metadata depends on aapt or aapt2 availability.",
            "Signing information depends on apksigner availability.",
            "Archive entry names alone do not establish malicious behaviour.",
        ],
    }

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Inspect APK metadata and archive structure."
    )

    parser.add_argument(
        "apk",
        type=Path,
        help="Path to the APK file.",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Optional JSON report destination.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting an existing output report.",
    )

    args = parser.parse_args()

    apk_path = args.apk.expanduser().resolve()

    if not apk_path.is_file():
        parser.error(f"APK does not exist: {apk_path}")

    if apk_path.is_symlink():
        parser.error("Symbolic-link APK inputs are not supported.")

    try:
        report = inspect_apk(apk_path)
        rendered = json.dumps(report, indent=4)

        if args.output:
            output = args.output.expanduser().resolve()

            if output == apk_path:
                parser.error("Output cannot overwrite the APK.")

            if output.exists() and not args.force:
                parser.error(
                    "Output exists. Use --force to overwrite it."
                )

            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered + "\n", encoding="utf-8")

            print(f"[+] Report saved: {output}")

        else:
            print(rendered)

        return 0

    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())