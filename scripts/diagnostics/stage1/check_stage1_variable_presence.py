"""
Stage 1 Diagnostic — Variable Presence Check (ERA5‑Correct, Stage 1→Stage 2‑Ready)
================================================================================

Purpose
-------
Verify that all required ERA5 variables are present in Stage 1 ingestion
outputs. This ensures Stage 2 normalization will not fail due to missing
or empty variables.

Checks performed:
    • required variable directories exist
    • at least one parquet file exists per variable
    • parquet files are readable
    • parquet files contain non-empty data
    • timestamps exist and are non-empty
    • latitude/longitude coverage is non-empty
    • variable column contains non-NaN values

Output
------
A JSON diagnostic report saved to:
    data/metadata/stage1_variable_presence.json
"""

import json
from pathlib import Path

import pandas as pd

# ------------------------------------------------------------------------------
# Required ERA5 variables for your pipeline
# ------------------------------------------------------------------------------

REQUIRED_VARIABLES = [
    "t2m", "d2m", "u10", "v10",
    "msl", "sp", "tcc",
    "blh", "cape", "cin",
    "tco3", "tcwv",
]

# ------------------------------------------------------------------------------
# Main diagnostic
# ------------------------------------------------------------------------------

def run_stage1_variable_presence(stage1_dir: str, output_path: str) -> None:
    print("[Stage 1][variable_presence] Checking Stage 1 variable outputs")

    base = Path(stage1_dir)
    results = {}

    for var in REQUIRED_VARIABLES:
        var_dir = base / var

        # Directory existence
        if not var_dir.exists():
            results[var] = {
                "exists": False,
                "files_present": False,
                "nonempty": False,
                "timestamps_present": False,
                "latlon_present": False,
                "variable_nonempty": False,
                "presence_pass": False,
                "error": f"Missing directory: {var_dir}",
            }
            continue

        # Parquet files
        parquet_files = list(var_dir.glob("*.parquet"))
        if len(parquet_files) == 0:
            results[var] = {
                "exists": True,
                "files_present": False,
                "nonempty": False,
                "timestamps_present": False,
                "latlon_present": False,
                "variable_nonempty": False,
                "presence_pass": False,
                "error": f"No parquet files found for variable {var}",
            }
            continue

        # Read first parquet file
        try:
            df = pd.read_parquet(parquet_files[0])
            readable = True
        except Exception as e:
            results[var] = {
                "exists": True,
                "files_present": True,
                "nonempty": False,
                "timestamps_present": False,
                "latlon_present": False,
                "variable_nonempty": False,
                "presence_pass": False,
                "error": f"Failed to read parquet: {e}",
            }
            continue

        # Row count
        nonempty = len(df) > 0

        # Timestamp presence
        timestamps_present = (
            "time" in df.columns and
            df["time"].notna().any()
        )

        # Lat/Lon presence
        latlon_present = (
            "latitude" in df.columns and df["latitude"].notna().any() and
            "longitude" in df.columns and df["longitude"].notna().any()
        )

        # Variable values
        variable_nonempty = (
            "value" in df.columns and
            df["value"].notna().any()
        )

        # Pass/fail
        presence_pass = (
            nonempty and
            timestamps_present and
            latlon_present and
            variable_nonempty
        )

        results[var] = {
            "exists": True,
            "files_present": True,
            "nonempty": nonempty,
            "timestamps_present": timestamps_present,
            "latlon_present": latlon_present,
            "variable_nonempty": variable_nonempty,
            "presence_pass": presence_pass,
        }

    # Save report
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(results, f, indent=2)

    print("[Stage 1][variable_presence] Report saved:", output_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stage 1 Variable Presence Diagnostic")
    parser.add_argument("--stage1", required=True, help="Path to Stage 1 output directory")
    parser.add_argument("--output", required=True, help="Path to write JSON report")

    args = parser.parse_args()
    run_stage1_variable_presence(args.stage1, args.output)
