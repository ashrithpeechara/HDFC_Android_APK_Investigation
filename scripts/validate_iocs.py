#!/usr/bin/env python3
"""
IOC Repository Validator

Validates JSON and CSV indicator files.

Checks:
    - JSON syntax and structure
    - CSV readability and headers
    - SHA-256 formatting
    - Duplicate indicator values
    - Empty indicator values
    - Basic IOC field consistency

This script performs local validation only.
It does not query external threat-intelligence services.
"""

import argparse
import csv
import json
import re
import sys

from collections import Counter
from pathlib import Path


SHA256_PATTERN = re.compile(r"^[a-fA-F0-9]{64}$")

EXPECTED_CSV_FIELDS = {
    "indicator_type",
    "indicator_value",
}


class ValidationResults:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []

    def error(self, message):
        self.errors.append(message)
        print(f"[ERROR] {message}")

    def warning(self, message):
        self.warnings.append(message)
        print(f"[WARN] {message}")

    def success(self, message):
        self.successes.append(message)
        print(f"[PASS] {message}")


def validate_sha256(value, location, results):
    """Validate a value when its field identifies it as SHA-256."""
    if not isinstance(value, str):
        results.error(f"{location}: SHA-256 value must be a string.")
        return

    if not SHA256_PATTERN.fullmatch(value):
        results.error(f"{location}: Invalid SHA-256 format.")
    else:
        results.success(f"{location}: Valid SHA-256 format.")


def walk_json(value, location, results, indicators):
    """Recursively inspect JSON values for hash fields and indicators."""
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"

            if isinstance(key, str) and (
                "sha256" in key.lower()
                or key.lower() in {"sha-256", "sha_256"}
            ):
                validate_sha256(child, child_location, results)

            if isinstance(child, (str, int, float)):
                normalized = str(child).strip()

                if normalized:
                    indicators.append(
                        (normalized.casefold(), child_location)
                    )

            walk_json(
                child,
                child_location,
                results,
                indicators,
            )

    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_json(
                child,
                f"{location}[{index}]",
                results,
                indicators,
            )


def validate_json_file(path, results):
    """Parse and validate a JSON file."""
    try:
        with path.open("r", encoding="utf-8") as stream:
            data = json.load(stream)

        results.success(f"{path}: Valid JSON syntax.")

        indicators = []
        walk_json(data, str(path), results, indicators)

        return indicators

    except json.JSONDecodeError as exc:
        results.error(
            f"{path}: JSON syntax error at line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        )

    except OSError as exc:
        results.error(f"{path}: Unable to read file: {exc}")

    return []


def validate_csv_file(path, results):
    """Validate CSV readability, headers, and indicator values."""
    indicators = []

    try:
        with path.open(
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as stream:

            reader = csv.DictReader(stream)

            if not reader.fieldnames:
                results.error(f"{path}: CSV header is missing.")
                return indicators

            fields = {
                field.strip().lower()
                for field in reader.fieldnames
                if field
            }

            missing = EXPECTED_CSV_FIELDS - fields

            if missing:
                results.warning(
                    f"{path}: Expected IOC columns not found: "
                    f"{', '.join(sorted(missing))}. "
                    "Checking available columns instead."
                )
            else:
                results.success(f"{path}: Expected IOC headers found.")

            value_column = next(
                (
                    field for field in reader.fieldnames
                    if field.strip().lower() == "indicator_value"
                ),
                None,
            )

            type_column = next(
                (
                    field for field in reader.fieldnames
                    if field.strip().lower() == "indicator_type"
                ),
                None,
            )

            if not value_column:
                results.error(
                    f"{path}: No indicator_value column found."
                )
                return indicators

            for row_number, row in enumerate(reader, start=2):
                value = (row.get(value_column) or "").strip()

                if not value:
                    results.error(
                        f"{path}: Empty indicator at row {row_number}."
                    )
                    continue

                indicator_type = (
                    (row.get(type_column) or "").strip().lower()
                    if type_column else ""
                )

                if indicator_type in {
                    "sha256",
                    "sha-256",
                    "file_hash",
                    "hash",
                }:
                    validate_sha256(
                        value,
                        f"{path}:row {row_number}",
                        results,
                    )

                indicators.append(
                    (value.casefold(), f"{path}:row {row_number}")
                )

        results.success(f"{path}: CSV file parsed successfully.")

    except (OSError, csv.Error) as exc:
        results.error(f"{path}: CSV processing failed: {exc}")

    return indicators


def check_duplicates(indicators, results):
    """Report duplicate indicator values."""
    counts = Counter(value for value, _ in indicators)

    for value, count in counts.items():
        if count > 1:
            locations = [
                location
                for item, location in indicators
                if item == value
            ]

            results.warning(
                f"Duplicate indicator ({count} occurrences): "
                f"{value[:80]} | Locations: {', '.join(locations)}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Validate repository IOC JSON and CSV files."
    )

    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="JSON or CSV files/directories to validate.",
    )

    args = parser.parse_args()

    results = ValidationResults()
    all_indicators = []
    files_checked = 0

    for supplied_path in args.paths:
        path = supplied_path.expanduser()

        if not path.exists():
            results.error(f"Path does not exist: {path}")
            continue

        if path.is_symlink():
            results.warning(f"Skipping symbolic link: {path}")
            continue

        if path.is_dir():
            files = sorted(
                item for item in path.rglob("*")
                if item.is_file() and not item.is_symlink()
            )
        else:
            files = [path]

        for file_path in files:
            suffix = file_path.suffix.lower()

            if suffix == ".json":
                files_checked += 1
                all_indicators.extend(
                    validate_json_file(file_path, results)
                )

            elif suffix == ".csv":
                files_checked += 1
                all_indicators.extend(
                    validate_csv_file(file_path, results)
                )

    check_duplicates(all_indicators, results)

    print("\n========== VALIDATION SUMMARY ==========")
    print(f"Files checked: {files_checked}")
    print(f"Successful checks: {len(results.successes)}")
    print(f"Warnings: {len(results.warnings)}")
    print(f"Errors: {len(results.errors)}")

    if results.errors:
        print("\nValidation completed with errors.")
        return 1

    print("\nValidation completed without errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())