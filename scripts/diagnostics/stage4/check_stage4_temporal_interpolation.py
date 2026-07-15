"""
Stage 4 Diagnostic — Temporal Interpolation Integrity Check (ERA5‑Correct, Stage 4‑Ready)
=========================================================================================

Purpose
-------
Validate the temporal interpolation invariant in Stage 4.

This diagnostic verifies:
    • number of interpolated timestamps
    • fraction of timestamps interpolated
    • per-variable interpolation spike counts
    • per-variable plateau counts
    • per-variable NaNs after interpolation
    • interpolation pass/fail criteria

Outputs
-------
A JSON diagnostic report saved to:
    data/spatiotemporal/stage4_temporal_interpolation_report.json

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

def _count_interpolated_timestamps(original_time, aligned_time):
    """Count timestamps added during interpolation."""
    original_set = set(original_time.tolist())
    aligned_set = set(aligned_time.tolist())
    return int(len(aligned_set - original_set))


def _compute_interpolated_fraction(original_time, aligned_time):
    """Fraction of timestamps that were interpolated."""
    added = _count_interpolated_timestamps(original_time, aligned_time)
    return float(added) / float(len(aligned_time))


def _detect_spikes(arr: np.ndarray, threshold: float = 5.0) -> int:
    """
    Detect interpolation spikes.

    Spike definition:
        abs(diff) > threshold * median(abs(diff))
    """
    diffs = np.abs(np.diff(arr))
    if diffs.size == 0:
        return 0

    median_diff = np.median(diffs)
    if median_diff == 0:
        return 0

    return int(np.sum(diffs > threshold * median_diff))


def _detect_plateaus(arr: np.ndarray, length: int = 3) -> int:
    """
    Detect interpolation plateaus.

    Plateau definition:
        run of identical values of length >= `length`
    """
    count = 0
    run = 1

    for i in range(1, arr.size):
        if arr[i] == arr[i - 1]:
            run += 1
        else:
            if run >= length:
                count += 1
            run = 1

    if run >= length:
        count += 1

    return int(count)


# ------------------------------------------------------------------------------
# Diagnostic entry point
# ------------------------------------------------------------------------------

def run_temporal_interpolation_diagnostic(dataset_path: str, output_path: str) -> None:
    """
    Run Stage 4 temporal interpolation diagnostic.

    Parameters
    ----------
    dataset_path : str
        Path to Stage 4 dataset (after temporal_interpolate.py).
    output_path : str
        Path to write diagnostic JSON report.
    """

    print("[Stage 4][interp_diag] Loading dataset:", dataset_path)
    ds = xr.open_dataset(dataset_path)

    time = ds["time"].values

    # --------------------------------------------------------------------------
    # Reconstruct original_time from NetCDF‑safe attributes
    # --------------------------------------------------------------------------

    required = ["original_time_min", "original_time_max", "original_time_len"]
    missing = [k for k in required if k not in ds.attrs]

    if missing:
        raise ValueError(f"[Stage 4][interp_diag] Missing required original_time attrs: {missing}")

    orig_min = np.datetime64(ds.attrs["original_time_min"])
    orig_max = np.datetime64(ds.attrs["original_time_max"])
    orig_len = int(ds.attrs["original_time_len"])

    # Convert datetime64 → int64 nanoseconds
    orig_min_ns = orig_min.astype("datetime64[ns]").astype(np.int64)
    orig_max_ns = orig_max.astype("datetime64[ns]").astype(np.int64)

    # Generate evenly spaced timestamps in integer space
    orig_ns = np.linspace(orig_min_ns, orig_max_ns, orig_len).astype(np.int64)

    # Convert back to datetime64
    original_time = orig_ns.astype("datetime64[ns]")

    # --------------------------------------------------------------------------
    # Compute interpolation diagnostics
    # --------------------------------------------------------------------------

    added_timestamps = _count_interpolated_timestamps(original_time, time)
    interpolated_fraction = _compute_interpolated_fraction(original_time, time)

    per_variable_spikes = {}
    per_variable_plateaus = {}
    per_variable_nan_after_interp = {}

    for var in ds.data_vars:
        if var == "mask":
            continue

        arr = ds[var].values

        # Flatten time × lat × lon into time × N
        arr_flat = arr.reshape(arr.shape[0], -1)

        spikes = 0
        plateaus = 0
        nan_after_interp = 0

        for t in range(arr_flat.shape[0]):
            row = arr_flat[t]

            spikes += _detect_spikes(row)
            plateaus += _detect_plateaus(row)
            nan_after_interp += int(np.sum(np.isnan(row)))

        per_variable_spikes[var] = spikes
        per_variable_plateaus[var] = plateaus
        per_variable_nan_after_interp[var] = nan_after_interp

    # Pass criteria
    interp_pass = (
        interpolated_fraction < 0.10  # less than 10% interpolated
        and all(v == 0 for v in per_variable_nan_after_interp.values())
    )

    # --------------------------------------------------------------------------
    # Build report
    # --------------------------------------------------------------------------

    report = {
        "added_timestamps": added_timestamps,
        "interpolated_fraction": interpolated_fraction,
        "per_variable_spikes": per_variable_spikes,
        "per_variable_plateaus": per_variable_plateaus,
        "per_variable_nan_after_interp": per_variable_nan_after_interp,
        "interp_pass": interp_pass,
    }

    # --------------------------------------------------------------------------
    # Save report
    # --------------------------------------------------------------------------

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print("[Stage 4][interp_diag] Report saved:", output_path)
    print("[Stage 4][interp_diag] interp_pass:", report["interp_pass"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stage 4 Temporal Interpolation Diagnostic")
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

    run_temporal_interpolation_diagnostic(args.dataset, args.output)
