"""
Stage 4 Diagnostic — QC Integrity Check (ERA5‑Correct, Stage 4‑Ready)
=====================================================================

Purpose
-------
Validate the QC invariant produced in Stage 4.

This diagnostic verifies:
    • total NaN count across all variables
    • total Inf count across all variables
    • total outlier count (robust MAD-based)
    • per-variable NaN distribution
    • per-variable Inf distribution
    • per-variable outlier distribution
    • QC pass/fail criteria

Outputs
-------
A JSON diagnostic report saved to:
    data/spatiotemporal/stage4_qc_report.json

Consumed by:
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

def _count_nans(arr: np.ndarray) -> int:
    """Count NaN values."""
    return int(np.sum(np.isnan(arr)))


def _count_infs(arr: np.ndarray) -> int:
    """Count Inf values."""
    return int(np.sum(np.isinf(arr)))


def _count_outliers(arr: np.ndarray, threshold: float = 5.0) -> int:
    """
    Count outliers using a robust z-score method.

    Outlier definition:
        abs(arr - median) / MAD > threshold
    """
    flat = arr.flatten()
    flat = flat[~np.isnan(flat)]
    if flat.size == 0:
        return 0

    median = np.median(flat)
    mad = np.median(np.abs(flat - median))

    if mad == 0:
        return 0

    z = np.abs(flat - median) / mad
    return int(np.sum(z > threshold))


# ------------------------------------------------------------------------------
# Diagnostic entry point
# ------------------------------------------------------------------------------

def run_qc_diagnostic(dataset_path: str, output_path: str) -> None:
    """
    Run Stage 4 QC diagnostic.

    Parameters
    ----------
    dataset_path : str
        Path to Stage 4 dataset (after QC.py).
    output_path : str
        Path to write diagnostic JSON report.
    """

    print("[Stage 4][qc_diag] Loading dataset:", dataset_path)
    ds = xr.open_dataset(dataset_path)

    # ----------------------------------------------------------------------
    # Per-variable QC metrics
    # ----------------------------------------------------------------------

    per_variable_nan = {}
    per_variable_inf = {}
    per_variable_outliers = {}

    total_nan = 0
    total_inf = 0
    total_outliers = 0

    for var in ds.data_vars:
        # mask is not a physical variable → skip
        if var == "mask":
            continue

        arr = ds[var].values

        nan_count = _count_nans(arr)
        inf_count = _count_infs(arr)
        outlier_count = _count_outliers(arr)

        per_variable_nan[var] = nan_count
        per_variable_inf[var] = inf_count
        per_variable_outliers[var] = outlier_count

        total_nan += nan_count
        total_inf += inf_count
        total_outliers += outlier_count

    # ----------------------------------------------------------------------
    # Pass criteria
    # ----------------------------------------------------------------------

    qc_pass = (
        total_nan == 0
        and total_inf == 0
        and total_outliers < 100   # configurable threshold
    )

    # ----------------------------------------------------------------------
    # Build report
    # ----------------------------------------------------------------------

    report = {
        "total_nan": total_nan,
        "total_inf": total_inf,
        "total_outliers": total_outliers,
        "per_variable_nan": per_variable_nan,
        "per_variable_inf": per_variable_inf,
        "per_variable_outliers": per_variable_outliers,
        "qc_pass": qc_pass,
    }

    # ----------------------------------------------------------------------
    # Save report
    # ----------------------------------------------------------------------

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print("[Stage 4][qc_diag] Report saved:", output_path)
    print("[Stage 4][qc_diag] qc_pass:", report["qc_pass"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stage 4 QC Diagnostic")
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

    run_qc_diagnostic(args.dataset, args.output)
