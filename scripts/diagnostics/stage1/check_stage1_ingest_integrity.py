"""
Stage 1 Diagnostic — Ingestion Integrity Check (ERA5‑Correct, Stage 1→Stage 2‑Ready)
====================================================================================

Purpose
-------
Validate the integrity of Stage 1 ingestion outputs (per-variable parquet files).
This diagnostic ensures that Stage 1 produced structurally valid, usable data
before Stage 2 normalization begins.

Checks performed:
    • file existence and readability
    • required schema columns present
    • no unexpected columns
    • correct dtypes
    • non-empty data
    • timestamp monotonicity
    • no duplicate timestamps
    • lat/lon bounds valid
    • variable column contains non-NaN values

Output
------
A JSON diagnostic report saved to:
    data/metadata/stage1_ingest_integrity_<variable>.json
"""

import json
from pathlib import Path

import pandas as pd

# ------------------------------------------------------------------------------
# Expected Stage 1 schema
# ------------------------------------------------------------------------------

REQUIRED_COLUMNS = {
    "time": "datetime64[ns]",
    "latitude": "float64",
    "longitude": "float64",
    "value": "float64",
}

# ------------------------------------------------------------------------------
# Main diagnostic
# ------------------------------------------------------------------------------


def run_stage1_ingest_integrity(parquet_path: str, output_path: str) -> None:
    print("[Stage 1][ingest_integrity] Checking:", parquet_path)

    path = Path(parquet_path)
    if not path.exists():
        report = {
            "file": path.name,
            "exists": False,
            "readable": False,
            "schema_ok": False,
            "row_count": 0,
            "timestamp_monotonic": False,
            "duplicate_timestamps": None,
            "latlon_bounds_ok": False,
            "variable_nonempty": False,
            "ingest_pass": False,
            "error": f"File not found: {parquet_path}",
        }
        _save_report(report, output_path)
        return

    # Try reading parquet
    try:
        df = pd.read_parquet(path)
        readable = True
    except Exception as e:
        report = {
            "file": path.name,
            "exists": True,
            "readable": False,
            "schema_ok": False,
            "row_count": 0,
            "timestamp_monotonic": False,
            "duplicate_timestamps": None,
            "latlon_bounds_ok": False,
            "variable_nonempty": False,
            "ingest_pass": False,
            "error": f"Failed to read parquet: {e}",
        }
        _save_report(report, output_path)
        return

    # Schema check
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    unexpected_cols = [c for c in df.columns if c not in REQUIRED_COLUMNS]

    dtype_ok = all(
        str(df[c].dtype) == REQUIRED_COLUMNS[c]
        for c in REQUIRED_COLUMNS
        if c in df.columns
    )

    schema_ok = (len(missing_cols) == 0) and dtype_ok

    # Row count
    row_count = len(df)

    # Timestamp checks
    timestamp_monotonic = df["time"].is_monotonic_increasing
    duplicate_timestamps = int(df["time"].duplicated().sum())

    # Lat/Lon bounds
    lat_ok = df["latitude"].between(-90, 90).all()
    lon_ok = df["longitude"].between(-180, 180).all()
    latlon_bounds_ok = lat_ok and lon_ok

    # Variable non-empty
    variable_nonempty = df["value"].notna().any()

    # Pass/fail
    ingest_pass = (
        readable
        and schema_ok
        and row_count > 0
        and timestamp_monotonic
        and duplicate_timestamps == 0
        and latlon_bounds_ok
        and variable_nonempty
    )

    # Build report
    report = {
        "file": path.name,
        "exists": True,
        "readable": readable,
        "schema_ok": schema_ok,
        "missing_columns": missing_cols,
        "unexpected_columns": unexpected_cols,
        "dtype_ok": dtype_ok,
        "row_count": row_count,
        "timestamp_monotonic": timestamp_monotonic,
        "duplicate_timestamps": duplicate_timestamps,
        "latlon_bounds_ok": latlon_bounds_ok,
        "variable_nonempty": variable_nonempty,
        "ingest_pass": ingest_pass,
    }

    _save_report(report, output_path)
    print("[Stage 1][ingest_integrity] Report saved:", output_path)
    print("[Stage 1][ingest_integrity] ingest_pass:", ingest_pass)


# ------------------------------------------------------------------------------
# Helper: save JSON report
# ------------------------------------------------------------------------------


def _save_report(report: dict, output_path: str) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Stage 1 Ingestion Integrity Diagnostic"
    )
    parser.add_argument("--parquet", required=True, help="Path to Stage 1 parquet file")
    parser.add_argument("--output", required=True, help="Path to write JSON report")

    args = parser.parse_args()
    run_stage1_ingest_integrity(args.parquet, args.output)
