"""
Stage 4 Diagnostic — Spatial Mask Integrity Check (ERA5‑Correct, Stage 4‑Ready)
===============================================================================

Purpose
-------
Validate the spatial mask produced in Stage 4.

This diagnostic verifies:
    • mask presence
    • mask shape consistency with lat/lon grid
    • valid fraction (percentage of True values)
    • hole count (isolated False pixels surrounded by True)
    • contiguity of mask (connected True region)
    • degenerate masks (all True or all False)

Outputs
-------
A JSON diagnostic report saved to:
    data/spatiotemporal/stage4_mask_report.json

Consumed by:
    • Stage 4 integration diagnostics
    • Stage 5 model readiness checks
"""

import json
from pathlib import Path
from typing import cast

import numpy as np
import xarray as xr
from scipy.ndimage import label

# ------------------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------------------


def _compute_valid_fraction(mask: np.ndarray) -> float:
    """Fraction of True values."""
    return float(np.mean(mask))


def _count_holes(mask: np.ndarray) -> int:
    """
    Count holes in the mask.

    A hole is:
        • a False pixel
        • surrounded by True pixels (4-connectivity)
    """
    holes = 0
    ny, nx = mask.shape

    for i in range(1, ny - 1):
        for j in range(1, nx - 1):
            if not mask[i, j]:
                neighbors = [
                    mask[i - 1, j],
                    mask[i + 1, j],
                    mask[i, j - 1],
                    mask[i, j + 1],
                ]
                if all(neighbors):
                    holes += 1

    return holes


def _count_contiguous_regions(mask: np.ndarray) -> int:
    """Count contiguous True regions using connected-component labeling."""
    labeled, num_regions = cast(tuple[np.ndarray, int], label(mask.astype(int)))
    return num_regions


# ------------------------------------------------------------------------------
# Diagnostic entry point
# ------------------------------------------------------------------------------


def run_mask_diagnostic(dataset_path: str, output_path: str) -> None:
    """
    Run Stage 4 spatial mask diagnostic.

    Parameters
    ----------
    dataset_path : str
        Path to Stage 4 dataset (after mask.py).
    output_path : str
        Path to write diagnostic JSON report.
    """

    print("[Stage 4][mask_diag] Loading dataset:", dataset_path)
    ds = xr.open_dataset(dataset_path)

    if "mask" not in ds:
        raise ValueError("[Stage 4][mask_diag] Dataset missing 'mask' variable")

    mask = ds["mask"].values

    # --------------------------------------------------------------------------
    # Shape consistency check
    # --------------------------------------------------------------------------

    if ("lat" not in ds) or ("lon" not in ds):
        raise ValueError("[Stage 4][mask_diag] Dataset missing lat/lon coordinates")

    lat = ds["lat"].values
    lon = ds["lon"].values

    if mask.shape != (lat.size, lon.size):
        raise ValueError(
            f"[Stage 4][mask_diag] Mask shape {mask.shape} does not match "
            f"lat/lon grid ({lat.size}, {lon.size})"
        )

    # --------------------------------------------------------------------------
    # Compute diagnostics
    # --------------------------------------------------------------------------

    valid_fraction = _compute_valid_fraction(mask)
    hole_count = _count_holes(mask)
    contiguous_regions = _count_contiguous_regions(mask)

    ny, nx = mask.shape

    mask_shape = {
        "ny": int(ny),
        "nx": int(nx),
    }

    # Degenerate mask detection
    all_true = bool(np.all(mask))
    all_false = bool(np.all(~mask))

    # Mask pass criteria
    mask_pass = (
        valid_fraction > 0.5
        and hole_count == 0
        and contiguous_regions == 1
        and not all_false
    )

    # --------------------------------------------------------------------------
    # Build report
    # --------------------------------------------------------------------------

    report = {
        "mask_shape": mask_shape,
        "valid_fraction": valid_fraction,
        "hole_count": hole_count,
        "contiguous_regions": contiguous_regions,
        "all_true": all_true,
        "all_false": all_false,
        "mask_pass": mask_pass,
    }

    # --------------------------------------------------------------------------
    # Save report
    # --------------------------------------------------------------------------

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print("[Stage 4][mask_diag] Report saved:", output_path)
    print("[Stage 4][mask_diag] mask_pass:", report["mask_pass"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stage 4 Mask Diagnostic")
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

    run_mask_diagnostic(args.dataset, args.output)
