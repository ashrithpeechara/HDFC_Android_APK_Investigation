#!/usr/bin/env python3
"""
SHA-256 Evidence Manifest Generator

Purpose:
    Generate cryptographic SHA-256 manifests for individual evidence
    files or recursively scanned directories.

Features:
    - Streaming SHA-256 calculation.
    - Recursive directory scanning.
    - CSV manifest generation.
    - File-size recording.
    - UTC timestamp recording.
    - Per-file error reporting.
    - Symbolic-link exclusion.
    - Existing-output protection.
    - Read-only source access.

Python:
    3.9+

Dependencies:
    Python standard library only.
"""

import argparse
import csv
import hashlib
import os
import sys

from datetime import datetime, timezone
from pathlib import Path


CHUNK_SIZE = 1024 * 1024  # 1 MiB


def get_utc_timestamp():
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def calculate_sha256(file_path):
    """
    Calculate SHA-256 using streaming reads.

    Returns:
        Tuple: (sha256_digest, file_size_bytes)
    """
    digest = hashlib.sha256()
    file_size = 0

    with file_path.open("rb") as file:
        while True:
            chunk = file.read(CHUNK_SIZE)

            if not chunk:
                break

            digest.update(chunk)
            file_size += len(chunk)

    return digest.hexdigest(), file_size


def iter_evidence_files(source):
    """Yield regular files without following symbolic links."""

    if source.is_symlink():
        raise ValueError("Symbolic-link sources are not supported.")

    if source.is_file():
        yield source
        return

    if not source.is_dir():
        raise ValueError(f"Invalid source path: {source}")

    for root, directories, filenames in os.walk(
        source,
        followlinks=False
    ):
        root_path = Path(root)

        directories[:] = [
            directory
            for directory in directories
            if not (root_path / directory).is_symlink()
        ]

        for filename in filenames:
            file_path = root_path / filename

            if file_path.is_symlink():
                continue

            if file_path.is_file():
                yield file_path


def generate_manifest(source, output):
    """Hash evidence files and generate manifest records."""

    records = []
    error_count = 0
    timestamp = get_utc_timestamp()

    for file_path in iter_evidence_files(source):

        if file_path.resolve() == output:
            continue

        try:
            file_hash, file_size = calculate_sha256(file_path)

            if source.is_dir():
                relative_path = file_path.relative_to(source).as_posix()
            else:
                relative_path = file_path.name

            records.append({
                "path": relative_path,
                "size_bytes": file_size,
                "sha256": file_hash,
                "status": "SUCCESS",
                "error": "",
                "collected_at_utc": timestamp,
            })

            print(f"[+] {relative_path}")
            print(f"    SHA256: {file_hash}")

        except OSError as exc:
            error_count += 1

            records.append({
                "path": str(file_path),
                "size_bytes": "",
                "sha256": "",
                "status": "ERROR",
                "error": str(exc),
                "collected_at_utc": timestamp,
            })

            print(
                f"[!] Failed to process {file_path}: {exc}",
                file=sys.stderr
            )

    return records, error_count


def write_manifest(records, output, force=False):
    """Write the evidence manifest to CSV."""

    if output.exists() and not force:
        raise FileExistsError(
            f"Manifest already exists: {output}. "
            "Use --force to overwrite."
        )

    output.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "path",
        "size_bytes",
        "sha256",
        "status",
        "error",
        "collected_at_utc",
    ]

    with output.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(records)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate a SHA-256 evidence manifest."
    )

    parser.add_argument(
        "source",
        type=Path,
        help="Evidence file or directory to process."
    )

    parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=Path,
        help="Destination CSV manifest."
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting an existing manifest."
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    source = args.source.expanduser()
    output = args.output.expanduser()

    if not source.exists():
        print(
            f"[ERROR] Source does not exist: {source}",
            file=sys.stderr
        )
        return 2

    if source.is_symlink():
        print(
            "[ERROR] Symbolic-link source is not supported.",
            file=sys.stderr
        )
        return 2

    try:
        source = source.resolve()
        output = output.resolve()

        if output == source:
            print(
                "[ERROR] Output cannot overwrite the source.",
                file=sys.stderr
            )
            return 2

        if source.is_dir() and output.is_relative_to(source):
            print(
                "[ERROR] Keep the manifest outside the scanned directory.",
                file=sys.stderr
            )
            return 2

        print("=" * 55)
        print("SHA-256 EVIDENCE MANIFEST GENERATOR")
        print("=" * 55)
        print(f"Source : {source}")
        print(f"Output : {output}")
        print("Mode   : Read-only source examination")
        print("=" * 55)

        records, errors = generate_manifest(source, output)

        write_manifest(records, output, args.force)

        successful = sum(
            record["status"] == "SUCCESS"
            for record in records
        )

        print("\n========== SUMMARY ==========")
        print(f"Files processed : {len(records)}")
        print(f"Successful      : {successful}")
        print(f"Errors          : {errors}")
        print(f"Manifest        : {output}")

        return 1 if errors else 0

    except (OSError, ValueError, FileExistsError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())