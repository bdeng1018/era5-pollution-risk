"""
Stage 1 Diagnostic — GRIB Metadata Check (ERA5‑Correct, Stage 1→Stage 2‑Ready)
===============================================================================

Purpose
-------
Inspect a GRIB file and extract metadata required by Stage 2 normalization.
This diagnostic does NOT load full arrays; it only inspects GRIB message
headers using eccodes.

Checks performed:
    • count GRIB messages
    • extract variable names (shortName)
    • extract level information
    • extract stepType (instant, accum, etc.)
    • extract grid geometry (lat/lon bounds, nx/ny)
    • detect multi-variable GRIBs
    • detect missing or malformed keys

Output
------
A JSON diagnostic report saved to:
    data/metadata/stage1_<filename>_metadata.json
"""

import json
from pathlib import Path

from eccodes import (
    codes_get,
    codes_get_array,
    codes_grib_new_from_file,
    codes_release,
)

# ------------------------------------------------------------------------------
# Helper: safe GRIB key getter
# ------------------------------------------------------------------------------

def _safe_get(handle, key):
    try:
        return codes_get(handle, key)
    except Exception:
        return None

def _safe_get_array(handle, key):
    try:
        return codes_get_array(handle, key)
    except Exception:
        return None

# ------------------------------------------------------------------------------
# Main diagnostic
# ------------------------------------------------------------------------------

def run_stage1_grib_metadata(grib_path: str, output_path: str) -> None:
    print("[Stage 1][metadata_diag] Inspecting GRIB:", grib_path)

    path = Path(grib_path)
    if not path.exists():
        raise FileNotFoundError(f"GRIB file not found: {grib_path}")

    variables = set()
    levels = set()
    step_types = set()

    message_count = 0
    first_handle = None

    with open(path, "rb") as f:
        while True:
            handle = codes_grib_new_from_file(f)
            if handle is None:
                break

            message_count += 1

            # Extract metadata
            variables.add(_safe_get(handle, "shortName"))
            levels.add(_safe_get(handle, "level"))
            step_types.add(_safe_get(handle, "stepType"))

            # Save first handle for grid geometry
            if first_handle is None:
                first_handle = handle
            else:
                codes_release(handle)

    if first_handle is None:
        raise ValueError("GRIB file contains no messages")

    # Grid geometry
    ny = _safe_get(first_handle, "Nj")
    nx = _safe_get(first_handle, "Ni")
    lat_min = _safe_get(first_handle, "latitudeOfFirstGridPointInDegrees")
    lat_max = _safe_get(first_handle, "latitudeOfLastGridPointInDegrees")
    lon_min = _safe_get(first_handle, "longitudeOfFirstGridPointInDegrees")
    lon_max = _safe_get(first_handle, "longitudeOfLastGridPointInDegrees")

    missing_keys = [
        key for key in [
            "Nj", "Ni",
            "latitudeOfFirstGridPointInDegrees",
            "latitudeOfLastGridPointInDegrees",
            "longitudeOfFirstGridPointInDegrees",
            "longitudeOfLastGridPointInDegrees",
        ]
        if _safe_get(first_handle, key) is None
    ]

    codes_release(first_handle)

    # Multi-variable detection
    multi_variable = len(variables) > 1

    # Pass/fail
    metadata_pass = (
        message_count > 0 and
        len(variables) > 0 and
        len(missing_keys) == 0
    )

    # Build report
    report = {
        "file": path.name,
        "message_count": message_count,
        "variables": sorted(v for v in variables if v is not None),
        "levels": sorted(l for l in levels if l is not None),
        "step_types": sorted(s for s in step_types if s is not None),
        "grid": {
            "ny": ny,
            "nx": nx,
            "lat_min": lat_min,
            "lat_max": lat_max,
            "lon_min": lon_min,
            "lon_max": lon_max,
        },
        "missing_keys": missing_keys,
        "multi_variable": multi_variable,
        "metadata_pass": metadata_pass,
    }

    # Save
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(report, f, indent=2)

    print("[Stage 1][metadata_diag] Report saved:", output_path)
    print("[Stage 1][metadata_diag] metadata_pass:", metadata_pass)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stage 1 GRIB Metadata Diagnostic")
    parser.add_argument("--grib", required=True, help="Path to GRIB file")
    parser.add_argument("--output", required=True, help="Path to write JSON report")

    args = parser.parse_args()
    run_stage1_grib_metadata(args.grib, args.output)
