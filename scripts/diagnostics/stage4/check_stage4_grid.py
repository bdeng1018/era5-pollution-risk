"""
Stage 4 Diagnostic — Grid Integrity Check (ERA5‑Correct, Stage 4‑Ready)
=======================================================================

Purpose
-------
Validate the spatial grid used in Stage 4 before tensor construction.

This diagnostic verifies:
    • latitude monotonicity
    • longitude monotonicity
    • uniform grid spacing
    • grid shape consistency
    • min/max lat/lon ranges
    • CRS assumptions (ERA5 uses a regular lat/lon grid)
    • detection of flipped or irregular grids

Outputs
-------
A JSON diagnostic report saved to:
    data/spatiotemporal/stage4_grid_report.json

This report is consumed by:
    • Stage 4 integration diagnostics
    • Stage 5 model readiness checks
"""

import json
from pathlib import Path

import numpy as np
import xarray as xr

# ------------------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------------------

def _is_monotonic(arr: np.ndarray) -> bool:
    """Check if array is strictly monotonic increasing."""
    return bool(np.all(np.diff(arr) > 0))


def _grid_spacing(arr: np.ndarray) -> float:
    """Compute median spacing between coordinates."""
    diffs = np.diff(arr)
    return float(np.median(diffs))


def _is_uniform_spacing(arr: np.ndarray, tol: float = 1e-6) -> bool:
    """Check if grid spacing is uniform within tolerance."""
    diffs = np.diff(arr)
    return bool(np.all(np.abs(diffs - diffs[0]) < tol))


# ------------------------------------------------------------------------------
# Diagnostic entry point
# ------------------------------------------------------------------------------

def run_grid_diagnostic(dataset_path: str, output_path: str) -> None:
    """
    Run Stage 4 grid integrity diagnostic.

    Parameters
    ----------
    dataset_path : str
        Path to Stage 4 dataset (merged.nc or aligned.nc).
    output_path : str
        Path to write diagnostic JSON report.
    """

    print("[Stage 4][grid_diag] Loading dataset:", dataset_path)
    ds = xr.open_dataset(dataset_path)

    lat = ds["lat"].values
    lon = ds["lon"].values

    # --------------------------------------------------------------------------
    # Compute diagnostics
    # --------------------------------------------------------------------------

    lat_monotonic = _is_monotonic(lat)
    lon_monotonic = _is_monotonic(lon)

    lat_spacing = _grid_spacing(lat)
    lon_spacing = _grid_spacing(lon)

    lat_uniform = _is_uniform_spacing(lat)
    lon_uniform = _is_uniform_spacing(lon)

    lat_min, lat_max = float(lat.min()), float(lat.max())
    lon_min, lon_max = float(lon.min()), float(lon.max())

    grid_shape = {
        "lat_count": lat.size,
        "lon_count": lon.size,
    }

    # ERA5 assumption: regular lat/lon grid
    crs_regular = lat_uniform and lon_uniform

    # --------------------------------------------------------------------------
    # Build report
    # --------------------------------------------------------------------------

    report = {
        "lat_monotonic": lat_monotonic,
        "lon_monotonic": lon_monotonic,
        "lat_uniform_spacing": lat_uniform,
        "lon_uniform_spacing": lon_uniform,
        "lat_spacing": lat_spacing,
        "lon_spacing": lon_spacing,
        "lat_min": lat_min,
        "lat_max": lat_max,
        "lon_min": lon_min,
        "lon_max": lon_max,
        "grid_shape": grid_shape,
        "crs_regular_latlon": crs_regular,
        "grid_pass": (
            lat_monotonic
            and lon_monotonic
            and lat_uniform
            and lon_uniform
            and crs_regular
        ),
    }

    # --------------------------------------------------------------------------
    # Save report
    # --------------------------------------------------------------------------

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print("[Stage 4][grid_diag] Report saved:", out_path)
    print("[Stage 4][grid_diag] grid_pass:", report["grid_pass"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stage 4 Grid Diagnostic")
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Path to Stage 4 dataset (e.g., spatiotemporal_tensor.nc)",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to write diagnostic JSON report",
    )

    args = parser.parse_args()

    run_grid_diagnostic(args.dataset, args.output)
