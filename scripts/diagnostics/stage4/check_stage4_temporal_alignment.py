"""
Stage 4 Diagnostic — Temporal Alignment Integrity Check (ERA5‑Correct, Stage 4‑Ready)
=====================================================================================

Purpose
-------
Validate the temporal alignment invariant in Stage 4.

This diagnostic verifies:
    • timestamp monotonicity
    • duplicate timestamp count
    • dominant temporal frequency (e.g., 1H, 12H)
    • stray intervals (intervals not equal to dominant frequency)
    • missing timestamps (based on dominant frequency)
    • aligned time axis length
    • alignment coverage (ratio of original timestamps to aligned timestamps)

Outputs
-------
A JSON diagnostic report saved to:
    data/spatiotemporal/stage4_temporal_alignment_report.json

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


def _is_monotonic(arr: np.ndarray) -> bool:
    """Check if array is strictly monotonic increasing."""
    return bool(np.all(np.diff(arr) > np.timedelta64(0, "h")))


def _compute_dominant_frequency(time: np.ndarray) -> int:
    """Compute dominant temporal frequency in hours."""
    diffs = np.diff(time).astype("timedelta64[h]").astype(int)
    if diffs.size == 0:
        return -1
    return int(np.bincount(diffs).argmax())


def _detect_stray_intervals(time: np.ndarray, freq_hours: int) -> int:
    """Count intervals that do not match the dominant frequency."""
    diffs = np.diff(time).astype("timedelta64[h]").astype(int)
    return int(np.sum(diffs != freq_hours))


def _detect_missing_timestamps(time: np.ndarray, freq_hours: int) -> int:
    """Count missing timestamps based on expected frequency."""
    diffs = np.diff(time).astype("timedelta64[h]").astype(int)
    missing = 0

    for d in diffs:
        if d > freq_hours:
            gap_count = d // freq_hours - 1
            missing += gap_count

    return int(missing)


def _build_aligned_time(time: np.ndarray, freq_hours: int) -> np.ndarray:
    """Build evenly spaced aligned timestamps."""
    start = time[0]
    end = time[-1]

    aligned = np.arange(
        start,
        end + np.timedelta64(freq_hours, "h"),
        np.timedelta64(freq_hours, "h"),
    )

    return aligned.astype("datetime64[ns]")


# ------------------------------------------------------------------------------
# Diagnostic entry point
# ------------------------------------------------------------------------------


def run_temporal_alignment_diagnostic(dataset_path: str, output_path: str) -> None:
    """
    Run Stage 4 temporal alignment diagnostic.

    Parameters
    ----------
    dataset_path : str
        Path to Stage 4 dataset (after mask.py).
    output_path : str
        Path to write diagnostic JSON report.
    """

    print("[Stage 4][temporal_align_diag] Loading dataset:", dataset_path)
    ds = xr.open_dataset(dataset_path)

    time = ds["time"].values

    # ----------------------------------------------------------------------
    # Compute diagnostics
    # ----------------------------------------------------------------------

    monotonic = _is_monotonic(time)

    # Duplicate timestamps
    duplicate_count = int(np.sum(np.diff(time) == np.timedelta64(0, "h")))

    # Dominant frequency
    freq_hours = _compute_dominant_frequency(time)

    # Stray intervals
    stray_intervals = _detect_stray_intervals(time, freq_hours)

    # Missing timestamps
    missing_count = _detect_missing_timestamps(time, freq_hours)

    # Build aligned timestamps
    aligned_time = _build_aligned_time(time, freq_hours)
    aligned_length = aligned_time.size

    # Alignment coverage
    coverage_ratio = float(time.size) / float(aligned_length)

    # Pass criteria
    temporal_pass = monotonic and duplicate_count == 0 and stray_intervals == 0

    # ----------------------------------------------------------------------
    # Build report
    # ----------------------------------------------------------------------

    report = {
        "monotonic": monotonic,
        "duplicate_count": duplicate_count,
        "dominant_frequency_hours": freq_hours,
        "stray_intervals": stray_intervals,
        "missing_timestamps": missing_count,
        "aligned_length": aligned_length,
        "original_length": int(time.size),
        "coverage_ratio": coverage_ratio,
        "temporal_pass": temporal_pass,
    }

    # ----------------------------------------------------------------------
    # Save report
    # ----------------------------------------------------------------------

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print("[Stage 4][temporal_align_diag] Report saved:", output_path)
    print("[Stage 4][temporal_align_diag] temporal_pass:", report["temporal_pass"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Stage 4 Temporal Alignment Diagnostic"
    )
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

    run_temporal_alignment_diagnostic(args.dataset, args.output)
