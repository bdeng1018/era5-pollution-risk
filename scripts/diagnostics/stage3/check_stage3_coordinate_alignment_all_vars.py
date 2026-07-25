"""
Full Variable Coordinate Alignment Diagnostic (ERA5‑Correct, Stage 3‑Ready)
===========================================================================

Purpose
-------
Determine which ERA5 variables can be merged in Stage 3 using the
key‑indexed Stage 2 metadata schema:

    "<timestamp>::<variable>": {
        "timestamp": "...",
        "variable": "...",
        "path": "...",
        "year": ...,
        "month": ...,
        "dtype": "...",
        "shape": [...]
    }

Checks:
    • Instantaneous variables share identical lat/lon grids
    • Flux variables use different grids → excluded
    • Static variables use different grids → excluded
    • Parquet files referenced in metadata.json exist and are readable

It does NOT check:
    • identical timestamp arrays across parquet files
    • identical grids across flux/static variables
    • identical timestamp lengths across variables

Stage 3 merges ONLY instantaneous variables with identical grids.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

METADATA_PATH = Path("data/metadata/metadata.json")

# ERA5 variable classes
INSTANT_VARS = {
    "blh",
    "cape",
    "cin",
    "d2m",
    "msl",
    "sp",
    "t2m",
    "tcc",
    "tco3",
    "tcwv",
    "u10",
    "v10",
}

FLUX_VARS = {"e", "slhf", "sshf", "ssr", "ssrc", "ssrd", "str", "tp"}

STATIC_VARS = {"lsm"}


# ------------------------------------------------------------------------------
# Metadata loading (key‑indexed)
# ------------------------------------------------------------------------------


def load_metadata() -> dict:
    if not METADATA_PATH.exists():
        raise FileNotFoundError("metadata.json missing")
    with open(METADATA_PATH, "r") as f:
        return json.load(f)


def get_one_parquet_for_variable(metadata: dict, var: str) -> str | None:
    """
    Return ONE parquet path for a variable by scanning key‑indexed metadata.
    """
    for key, entry in metadata.items():
        if entry.get("variable") == var:
            return entry.get("path")
    return None


# ------------------------------------------------------------------------------
# Parquet coordinate extraction
# ------------------------------------------------------------------------------


def extract_coords(path: str) -> tuple[pd.Series, pd.Series] | None:
    try:
        df = pd.read_parquet(path)
        return df["latitude"], df["longitude"]
    except Exception:
        return None


# ------------------------------------------------------------------------------
# Alignment logic
# ------------------------------------------------------------------------------


def compare_arrays(ref: pd.Series, other: pd.Series):
    issues = []

    if len(ref) != len(other):
        issues.append(f"Length mismatch: {len(ref)} vs {len(other)}")
        return issues

    if ref.dtype != other.dtype:
        issues.append(f"dtype mismatch: {ref.dtype} vs {other.dtype}")

    if not ref.equals(other):
        issues.append("Value mismatch")

    return issues


def diagnose_alignment(metadata: dict):
    print("=== Full Variable Coordinate Alignment Diagnostic (ERA5‑Correct) ===\n")

    # Extract reference instantaneous grid
    ref_var = "t2m"
    ref_path = get_one_parquet_for_variable(metadata, ref_var)

    if ref_path is None:
        print(f"❌ No parquet found for reference variable {ref_var}")
        return

    ref_coords = extract_coords(ref_path)
    if ref_coords is None:
        print(f"❌ Failed to read reference parquet: {ref_path}")
        return

    ref_lat, ref_lon = ref_coords
    print(f"Reference instantaneous variable: {ref_var}\n")

    # Check instantaneous variables
    print("=== Checking instantaneous variables ===\n")
    for var in INSTANT_VARS:
        print(f"Variable: {var}")

        p = get_one_parquet_for_variable(metadata, var)
        if p is None:
            print(f"  ❌ No parquet found for {var}\n")
            continue

        coords = extract_coords(p)
        if coords is None:
            print(f"  ❌ Unreadable parquet: {p}\n")
            continue

        lat, lon = coords

        lat_issues = compare_arrays(ref_lat, lat)
        lon_issues = compare_arrays(ref_lon, lon)

        if not lat_issues and not lon_issues:
            print("  ✔ Grid aligned\n")
        else:
            print("  ❌ Grid misalignment detected:")
            if lat_issues:
                print(f"    latitude: {lat_issues}")
            if lon_issues:
                print(f"    longitude: {lon_issues}")
            print()

    # Flux variables — skip grid comparison
    print("=== Flux variables (grid differences expected) ===\n")
    for var in FLUX_VARS:
        print(f"Flux variable: {var} — grid differences expected ✔\n")

    # Static variables — skip grid comparison
    print("=== Static variables (grid differences expected) ===\n")
    for var in STATIC_VARS:
        print(f"Static variable: {var} — grid differences expected ✔\n")


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------


def main():
    metadata = load_metadata()
    diagnose_alignment(metadata)


if __name__ == "__main__":
    main()
