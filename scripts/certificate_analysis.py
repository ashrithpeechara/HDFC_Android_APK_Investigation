#!/usr/bin/env python3
"""
Certificate Timeline Analyzer

Analyzes previously collected certificate-transparency records.

Capabilities:
    - Count certificate records and unique certificate IDs.
    - Count unique DNS names.
    - Identify repeated DNS names.
    - Calculate issuance intervals.
    - Compare public-key SHA-256 fingerprints.
    - Generate a structured JSON summary.

This script does not contact certificate-transparency services.

Expected input:
    JSON list or an object containing a certificates list.

Recognized fields:
    id / cert_id
    dns_names / names / san
    not_before / issued_at
    not_after / expires_at
    revoked
    pubkey_sha256
    cert_sha256

Python dependencies:
    Standard library only.
"""

import argparse
import hashlib
import json
import re
import statistics
import sys

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


SHA256_PATTERN = re.compile(r"^[a-fA-F0-9]{64}$")


def load_json(path):
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def parse_timestamp(value):
    """Parse ISO-8601 timestamps into timezone-aware UTC datetimes."""
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    except (ValueError, TypeError):
        return None


def normalize_names(value):
    """Normalize certificate DNS names."""
    if isinstance(value, str):
        names = [value]
    elif isinstance(value, list):
        names = value
    else:
        names = []

    return sorted({
        str(name).strip().lower().rstrip(".")
        for name in names
        if str(name).strip()
    })


def normalize_certificates(data):
    """Normalize recognized certificate record formats."""
    if isinstance(data, list):
        certificates = data
    elif isinstance(data, dict):
        certificates = data.get("certificates", data.get("results", []))
    else:
        raise ValueError("Unsupported certificate JSON structure.")

    if not isinstance(certificates, list):
        raise ValueError("Certificate records must be a list.")

    normalized = []

    for index, certificate in enumerate(certificates):
        if not isinstance(certificate, dict):
            print(
                f"[WARN] Skipping invalid certificate at index {index}.",
                file=sys.stderr,
            )
            continue

        cert_id = certificate.get("id") or certificate.get("cert_id")

        names = (
            certificate.get("dns_names")
            or certificate.get("names")
            or certificate.get("san")
            or []
        )

        issued = (
            certificate.get("not_before")
            or certificate.get("issued_at")
        )

        expires = (
            certificate.get("not_after")
            or certificate.get("expires_at")
        )

        normalized.append({
            "id": str(cert_id) if cert_id is not None else None,
            "dns_names": normalize_names(names),
            "issued_at": parse_timestamp(issued),
            "expires_at": parse_timestamp(expires),
            "revoked": certificate.get("revoked"),
            "pubkey_sha256": certificate.get("pubkey_sha256"),
            "cert_sha256": certificate.get("cert_sha256"),
        })

    return normalized


def analyze_certificates(certificates):
    """Calculate certificate statistics and repeated-name timelines."""
    certificate_ids = [
        certificate["id"]
        for certificate in certificates
        if certificate["id"] is not None
    ]

    dns_names = set()
    name_records = defaultdict(list)

    invalid_fingerprints = []

    for certificate in certificates:
        for name in certificate["dns_names"]:
            dns_names.add(name)
            name_records[name].append(certificate)

        for field in ("pubkey_sha256", "cert_sha256"):
            fingerprint = certificate.get(field)

            if fingerprint and not SHA256_PATTERN.fullmatch(str(fingerprint)):
                invalid_fingerprints.append({
                    "certificate_id": certificate["id"],
                    "field": field,
                    "value": fingerprint,
                })

    repeated_names = {}
    issuance_intervals_days = []

    for name, records in sorted(name_records.items()):
        ordered = sorted(
            [
                record for record in records
                if record["issued_at"] is not None
            ],
            key=lambda record: record["issued_at"],
        )

        if len(records) < 2:
            continue

        fingerprints = sorted({
            str(record["pubkey_sha256"]).lower()
            for record in records
            if record["pubkey_sha256"]
        })

        intervals = []

        for previous, current in zip(ordered, ordered[1:]):
            interval = (
                current["issued_at"] - previous["issued_at"]
            ).total_seconds() / 86400

            intervals.append(round(interval, 2))
            issuance_intervals_days.append(interval)

        repeated_names[name] = {
            "certificate_count": len(records),
            "certificate_ids": [
                record["id"] for record in records
            ],
            "distinct_public_key_fingerprints": len(fingerprints),
            "issuance_intervals_days": intervals,
        }

    average_interval = (
        round(statistics.mean(issuance_intervals_days), 2)
        if issuance_intervals_days else None
    )

    return {
        "total_certificate_records": len(certificates),
        "unique_certificate_ids": len(set(certificate_ids)),
        "unique_dns_names": len(dns_names),
        "repeated_dns_names": repeated_names,
        "repeated_dns_name_count": len(repeated_names),
        "average_repeated_name_issuance_interval_days": average_interval,
        "invalid_fingerprints": invalid_fingerprints,
    }


def build_report(source, certificates):
    analysis = analyze_certificates(certificates)

    return {
        "tool": "Certificate Timeline Analyzer",
        "analysis_type": "Offline certificate dataset analysis",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": source.name,
        "summary": analysis,
        "limitations": [
            "No certificate-transparency queries were performed.",
            "Results depend entirely on the supplied dataset.",
            "Incomplete collection can affect counts and issuance intervals.",
            "Certificate issuance does not establish domain ownership.",
            "Repeated certificates do not independently prove common operation.",
            "Different public keys do not prove that domains are unrelated.",
            "Certificate records do not establish current deployment.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze collected certificate records."
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input certificate JSON dataset.",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Optional output JSON report.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting an existing output report.",
    )

    args = parser.parse_args()

    source = args.input.expanduser().resolve()

    if not source.is_file():
        parser.error(f"Input file does not exist: {source}")

    try:
        data = load_json(source)
        certificates = normalize_certificates(data)

        report = build_report(source, certificates)
        rendered = json.dumps(report, indent=4)

        if args.output:
            output = args.output.expanduser().resolve()

            if output == source:
                parser.error("Output cannot overwrite the input dataset.")

            if output.exists() and not args.force:
                parser.error("Output exists. Use --force to overwrite.")

            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered + "\n", encoding="utf-8")

            print(f"[+] Report saved: {output}")

        else:
            print(rendered)

        summary = report["summary"]

        print("\n====== CERTIFICATE ANALYSIS SUMMARY ======")
        print(f"Certificate records: {summary['total_certificate_records']}")
        print(f"Unique certificate IDs: {summary['unique_certificate_ids']}")
        print(f"Unique DNS names: {summary['unique_dns_names']}")
        print(f"Repeated DNS names: {summary['repeated_dns_name_count']}")
        print(
            "Average issuance interval: "
            f"{summary['average_repeated_name_issuance_interval_days']} days"
        )

        return 0

    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())