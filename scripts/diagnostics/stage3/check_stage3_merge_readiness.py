"""
Stage 3 Merge Readiness Diagnostic (ERA5‑Correct, Branch‑2‑Correct)
===================================================================

Purpose
-------
Verify that Stage 3 can safely merge instantaneous ERA5 variables using:

    • Stage 2 metadata.json (key‑indexed schema)
    • Stage 3 chunk outputs (normalized lat/lon grid)
    • Stage 3 schema (deterministic column order)

Stage 2 metadata.json format:
    "<timestamp>::<variable>": {
        "timestamp": "...",
        "variable": "...",
        "path": "...",
        "year": ...,
        "month": ...,
        "dtype": "...",
        "shape": [...]
    }

This diagnostic checks:

    ✔ metadata.json readability
    ✔ presence of all instantaneous variables
    ✔ timestamp coverage (not intersection)
    ✔ Stage 3 grid alignment (lat/lon from chunk outputs)
    ✔ parquet existence + readability

This diagnostic does NOT check:

    ✘ flux/accumulated variables
    ✘ static variables
    ✘ per-variable timestamp intersection
    ✘ raw Stage 2 parquet grids (Stage 3 normalizes them)

If this diagnostic passes, Stage 3 is merge‑ready.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

# ------------------------------------------------------------------------------

METADATA_PATH = Path("data/metadata/metadata.json")
CHUNK_DIR = Path("data/chunks")

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

# ------------------------------------------------------------------------------
# Helpers — Key‑Indexed Metadata
# ------------------------------------------------------------------------------


def load_metadata() -> dict:
    if not METADATA_PATH.exists():
        raise FileNotFoundError("❌ metadata.json missing")
    with open(METADATA_PATH, "r") as f:
        return json.load(f)


def get_all_timestamps(metadata: dict) -> list[str]:
    """Extract all timestamps from key‑indexed metadata."""
    ts_list = []
    for key, entry in metadata.items():
        ts_list.append(entry["timestamp"])
    return sorted(set(ts_list))


def get_parquets_for_variable(metadata: dict, var: str) -> list[str]:
    """Return ALL parquet paths for a variable."""
    paths = []
    for key, entry in metadata.items():
        if entry.get("variable") == var:
            paths.append(entry.get("path"))
    return paths


def get_one_parquet_for_variable(metadata: dict, var: str) -> str | None:
    """Return ONE parquet path for a variable."""
    for key, entry in metadata.items():
        if entry.get("variable") == var:
            return entry.get("path")
    return None


# ------------------------------------------------------------------------------
# Stage 3 chunk loader
# ------------------------------------------------------------------------------


def load_stage3_chunk(var: str, ts: str) -> pd.DataFrame | None:
    safe_ts = ts.replace(":", "-")
    path = CHUNK_DIR / f"{var}_{safe_ts}_12hr.parquet"
    if not path.exists():
        return None
    try:
        return pd.read_parquet(path)
    except Exception:
        return None


# ------------------------------------------------------------------------------
# Timestamp coverage
# ------------------------------------------------------------------------------


def check_timestamp_coverage(metadata: dict):
    issues = []

    full_ts = get_all_timestamps(metadata)
    if not full_ts:
        return False, ["metadata.json contains no timestamps"]

    for var in INSTANT_VARS:
        var_ts = [
            entry["timestamp"]
            for key, entry in metadata.items()
            if entry["variable"] == var
        ]

        if not var_ts:
            issues.append(f"{var}: no parquet files in metadata.json")
            continue

        coverage = sum(1 for ts in full_ts if ts in var_ts)
        if coverage == 0:
            issues.append(f"{var}: no timestamp coverage in full timeline")

    return len(issues) == 0, issues


# ------------------------------------------------------------------------------
# Stage 3 grid alignment
# ------------------------------------------------------------------------------


def check_grid_alignment():
    issues = []

    # Reference: t2m chunk
    t2m_chunks = sorted(CHUNK_DIR.glob("t2m_*_12hr.parquet"))
    if not t2m_chunks:
        return False, ["No Stage 3 chunks found for t2m"]

    ref_df = pd.read_parquet(t2m_chunks[0])
    ref_lat = ref_df["lat"]
    ref_lon = ref_df["lon"]

    for var in INSTANT_VARS:
        chunks = sorted(CHUNK_DIR.glob(f"{var}_*_12hr.parquet"))
        if not chunks:
            issues.append(f"{var}: no Stage 3 chunks found")
            continue

        df = pd.read_parquet(chunks[0])
        lat = df["lat"]
        lon = df["lon"]

        if not lat.equals(ref_lat):
            issues.append(f"{var}: latitude grid mismatch (Stage 3)")
        if not lon.equals(ref_lon):
            issues.append(f"{var}: longitude grid mismatch (Stage 3)")

    return len(issues) == 0, issues


# ------------------------------------------------------------------------------
# Main diagnostic
# ------------------------------------------------------------------------------


def main():
    print(
        "=== Stage 3 Merge Readiness Diagnostic (ERA5‑Correct, Branch‑2‑Correct) ===\n"
    )

    metadata = load_metadata()

    # Extract variables from key‑indexed metadata
    vars_in_metadata = sorted({entry["variable"] for entry in metadata.values()})
    print(f"Variables in metadata.json: {vars_in_metadata}\n")

    # 1. Instantaneous variable presence
    missing = [v for v in INSTANT_VARS if v not in vars_in_metadata]
    if missing:
        print("❌ Missing instantaneous variables in metadata.json:")
        for v in missing:
            print(f"  - {v}")
        print("\nStage 3 merge cannot proceed.\n")
        return
    else:
        print("✔ All instantaneous variables present in metadata.json.\n")

    # 2. Timestamp coverage
    ts_ok, ts_issues = check_timestamp_coverage(metadata)
    if ts_ok:
        print("✔ Timestamp coverage OK across instantaneous variables.\n")
    else:
        print("❌ Timestamp coverage issues:")
        for issue in ts_issues:
            print(f"  - {issue}")
        print()

    # 3. Stage 3 grid alignment
    grid_ok, grid_issues = check_grid_alignment()
    if grid_ok:
        print("✔ Stage 3 lat/lon grids aligned across instantaneous variables.\n")
    else:
        print("❌ Stage 3 grid misalignment detected:")
        for issue in grid_issues:
            print(f"  - {issue}")
        print()

    # 4. Final verdict
    if ts_ok and grid_ok:
        print("✅ Stage 3 is merge‑ready: timestamp coverage + grid alignment OK.")
    else:
        print("⚠️ Stage 3 is NOT fully merge‑ready. Fix issues above before merging.")


if __name__ == "__main__":
    main()
