#!/usr/bin/env python3
"""
DNS Observation Analyzer

Summarizes previously collected DNS observations from a JSON file.

Supported input:
    - A records
    - AAAA records
    - CNAME records
    - MX records
    - NS records
    - TXT records
    - Other record types represented in the input JSON

This utility does not perform DNS lookups.
It only analyses locally supplied observations.

Python dependencies:
    Standard library only.
"""

import argparse
import json
import sys

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


SUPPORTED_RECORD_TYPES = {
    "A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA", "CAA"
}


def load_json(path):
    """Load a local JSON dataset."""
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def normalize_records(data):
    """
    Normalize supported DNS JSON structures into a record list.

    Supported examples:

    1. List:
       [{"name": "example.com", "type": "A", "value": "1.2.3.4"}]

    2. Object containing records:
       {"records": [...]}

    3. Object containing domains:
       {"domains": [...]}

    Each record should contain name, type and value fields.
    """
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        records = data.get("records", data.get("domains", []))
    else:
        raise ValueError("Unsupported JSON root structure.")

    if not isinstance(records, list):
        raise ValueError("DNS records must be represented as a list.")

    normalized = []

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            print(
                f"[WARN] Skipping invalid record at index {index}.",
                file=sys.stderr,
            )
            continue

        name = record.get("name") or record.get("domain")
        record_type = record.get("type") or record.get("record_type")
        value = record.get("value") or record.get("data") or record.get("content")

        if not name or not record_type or value is None:
            print(
                f"[WARN] Incomplete DNS record at index {index}.",
                file=sys.stderr,
            )
            continue

        normalized.append({
            "name": str(name).strip().lower().rstrip("."),
            "type": str(record_type).strip().upper(),
            "value": str(value).strip(),
            "ttl": record.get("ttl"),
            "source": record.get("source"),
            "observed_at": record.get("observed_at"),
        })

    return normalized


def analyze_records(records):
    """Generate DNS observation statistics."""
    type_counts = Counter()
    domain_records = defaultdict(list)
    unique_values = defaultdict(set)

    for record in records:
        record_type = record["type"]
        name = record["name"]
        value = record["value"]

        type_counts[record_type] += 1
        domain_records[name].append(record)
        unique_values[record_type].add(value)

    return {
        "total_records": len(records),
        "unique_domains": len(domain_records),
        "record_type_counts": dict(sorted(type_counts.items())),
        "unique_values_by_type": {
            record_type: len(values)
            for record_type, values in sorted(unique_values.items())
        },
        "domains": {
            name: domain_records[name]
            for name in sorted(domain_records)
        },
    }


def build_report(source, records):
    """Build a structured JSON report."""
    analysis = analyze_records(records)

    return {
        "tool": "DNS Observation Analyzer",
        "analysis_type": "Offline DNS dataset analysis",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": source.name,
        "summary": {
            "total_records": analysis["total_records"],
            "unique_domains": analysis["unique_domains"],
            "record_type_counts": analysis["record_type_counts"],
            "unique_values_by_type": analysis["unique_values_by_type"],
        },
        "domains": analysis["domains"],
        "limitations": [
            "No DNS queries were performed.",
            "Results depend entirely on the supplied dataset.",
            "Missing records cannot be interpreted as proof of absence.",
            "DNS observations do not independently identify infrastructure ownership.",
            "Cloudflare edge addresses must not be treated as origin addresses without independent evidence.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze previously collected DNS records."
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input DNS observations JSON file.",
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
        records = normalize_records(data)

        report = build_report(source, records)
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

        print("\n========== DNS ANALYSIS SUMMARY ==========")
        print(f"Records: {report['summary']['total_records']}")
        print(f"Unique domains: {report['summary']['unique_domains']}")

        for record_type, count in report["summary"]["record_type_counts"].items():
            print(f"{record_type}: {count}")

        return 0

    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())