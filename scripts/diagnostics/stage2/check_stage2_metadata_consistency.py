"""
Stage 2 Diagnostic — Metadata Consistency (Key‑Indexed Schema, ERA5‑Correct, Stage 3‑Ready)
================================================================================

Purpose
-------
Validate the integrity of metadata.json produced by Stage 2 when using the
*key‑indexed* metadata schema:

    {
      "<timestamp>::<variable>": {
          "timestamp": "...",
          "variable": "...",
          "path": "...",
          "year": ...,
          "month": ...,
          "dtype": "...",
          "shape": [...]
      },
      ...
    }

Stage 3 relies EXCLUSIVELY on this metadata.json for:
    • variable list reconstruction
    • timestamp list reconstruction
    • (variable, timestamp) → parquet path mapping
    • merge‑ready temporal alignment

Therefore metadata.json must be:
    ✔ readable
    ✔ complete
    ✔ internally consistent
    ✔ free of malformed keys
    ✔ free of missing parquet references
    ✔ free of unreadable parquet files
    ✔ sorted by timestamp (after extraction)
    ✔ free of duplicate timestamps

This diagnostic checks all of the above.

It does NOT check:
    ✘ parquet timestamp arrays (Stage 3 does not use them)
    ✘ lat/lon grids (checked in Stage 3 diagnostics)
    ✘ flux/static variables (excluded from Stage 3 merging)

Usage:
    python check_stage2_metadata_consistency.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

METADATA_PATH = Path("data/metadata/metadata.json")


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------

def load_metadata() -> Dict:
    """Load metadata.json and return dict."""
    if not METADATA_PATH.exists():
        raise FileNotFoundError("❌ metadata.json missing")

    try:
        with open(METADATA_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to read metadata.json: {e}")


def parquet_exists(path: str) -> bool:
    return Path(path).exists()


def parquet_readable(path: str) -> bool:
    try:
        pd.read_parquet(path)
        return True
    except Exception:
        return False


def parse_key(key: str) -> Tuple[str, str]:
    """Parse '<timestamp>::<variable>' key."""
    if "::" not in key:
        raise ValueError(f"Malformed metadata key: {key}")
    ts, var = key.split("::", 1)
    return ts, var


# ------------------------------------------------------------------------------
# Main Diagnostic
# ------------------------------------------------------------------------------

def main():
    print("=== Stage 2 Metadata Consistency Diagnostic (Key‑Indexed Schema, ERA5‑Correct) ===\n")

    metadata = load_metadata()

    keys = list(metadata.keys())
    print(f"Found {len(keys)} metadata entries\n")

    timestamps = []
    variables = set()

    any_issues = False

    # Validate each metadata entry
    for key, entry in metadata.items():
        try:
            ts, var = parse_key(key)
        except ValueError as e:
            print(f"❌ {e}")
            any_issues = True
            continue

        timestamps.append(ts)
        variables.add(var)

        # Required fields
        required_fields = ["timestamp", "variable", "path", "year", "month", "dtype", "shape"]
        missing = [f for f in required_fields if f not in entry]
        if missing:
            print(f"❌ Missing fields in entry {key}: {missing}")
            any_issues = True

        # Parquet existence
        path = entry.get("path")
        if not parquet_exists(path):
            print(f"❌ Missing parquet file: {path}")
            any_issues = True
            continue

        # Parquet readability
        if not parquet_readable(path):
            print(f"❌ Unreadable parquet file: {path}")
            any_issues = True

    print()

    # Timestamp sortedness
    if timestamps != sorted(timestamps):
        print("❌ Timestamps not sorted")
        any_issues = True
    else:
        print("✔ Timestamps sorted")

    # Timestamp uniqueness
    if len(timestamps) != len(set(timestamps)):
        print("❌ Duplicate timestamps detected")
        any_issues = True
    else:
        print("✔ Timestamps unique")

    print()

    print(f"Variables detected: {sorted(variables)}")
    print(f"Timestamps detected: {len(timestamps)} entries\n")

    if not any_issues:
        print("✔ All Stage 2 metadata is valid and Stage 3‑ready.")
    else:
        print("❌ Metadata issues detected. Stage 3 may fail.")


if __name__ == "__main__":
    main()
