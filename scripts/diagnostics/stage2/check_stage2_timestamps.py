"""
Stage 2 Timestamp Consistency Diagnostic (Key‑Indexed Schema, ERA5‑Correct)
===========================================================================

Purpose
-------
Validate Stage 2 timestamps using metadata.json when using the *key‑indexed*
metadata schema:

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

Stage 3 merging relies EXCLUSIVELY on metadata timestamps — NOT parquet
timestamp arrays — therefore metadata.json must be:

    ✔ readable
    ✔ complete
    ✔ sorted by timestamp (after extraction)
    ✔ free of duplicate timestamps
    ✔ free of missing parquet references
    ✔ free of unreadable parquet files
    ✔ free of malformed keys

This diagnostic checks all of the above.

It does NOT check:
    ✘ parquet timestamp arrays (Stage 3 does not use them)
    ✘ identical timestamp lengths across variables
    ✘ identical grids across variables

Usage:
    python check_stage2_timestamps.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

METADATA_PATH = Path("data/metadata/metadata.json")


# ------------------------------------------------------------------------------
# Metadata Loading
# ------------------------------------------------------------------------------


def load_metadata() -> dict:
    """Load metadata.json and return dict."""
    if not METADATA_PATH.exists():
        raise FileNotFoundError("❌ metadata.json missing")

    try:
        with open(METADATA_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to read metadata.json: {e}")


# ------------------------------------------------------------------------------
# Parquet Checks
# ------------------------------------------------------------------------------


def parquet_exists(path: str) -> bool:
    return Path(path).exists()


def parquet_readable(path: str) -> bool:
    try:
        pd.read_parquet(path)
        return True
    except Exception:
        return False


# ------------------------------------------------------------------------------
# Key Parsing
# ------------------------------------------------------------------------------


def parse_key(key: str) -> tuple[str, str]:
    """Parse '<timestamp>::<variable>' key."""
    if "::" not in key:
        raise ValueError(f"Malformed metadata key: {key}")
    ts, var = key.split("::", 1)
    return ts, var


# ------------------------------------------------------------------------------
# Main Diagnostic
# ------------------------------------------------------------------------------


def main():
    print(
        "=== Stage 2 Timestamp Consistency Diagnostic (Key‑Indexed Schema, ERA5‑Correct) ===\n"
    )

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
        required_fields = ["timestamp", "variable", "path"]
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
        print("✔ All Stage 2 timestamps are valid and Stage 3‑ready.")
    else:
        print("❌ Timestamp issues detected. Stage 3 may fail.")


if __name__ == "__main__":
    main()
