"""
Stage 4 – Temporal Alignment Invariant
======================================

Purpose
-------
Normalize and validate the temporal coordinate system for Stage 4.

Responsibilities
----------------
- Ensure time is strictly ascending
- Compute dominant temporal frequency
- Detect missing timestamps
- Build an evenly spaced aligned time axis
- Expand the dataset to include missing timestamps (filled with NaN)
- Produce a deterministic temporal metadata contract
- Do NOT interpolate values (interpolation is Stage 4 temporal_interpolate)
"""

from collections.abc import Mapping
from typing import Any

import numpy as np
import xarray as xr

# ------------------------------------------------------------------------------
# Utility checks
# ------------------------------------------------------------------------------


def _is_strictly_ascending(arr: np.ndarray) -> bool:
    return bool(np.all(np.diff(arr) > 0))


# ------------------------------------------------------------------------------
# Normalization
# ------------------------------------------------------------------------------


def normalize_time(ds: xr.Dataset) -> xr.Dataset:
    """Ensure time is sorted ascending."""
    time = ds["time"].values
    if not _is_strictly_ascending(time):
        return ds.sortby("time")
    return ds


# ------------------------------------------------------------------------------
# Frequency detection
# ------------------------------------------------------------------------------


def compute_frequency(time: np.ndarray) -> str:
    """Compute dominant temporal frequency in hours."""
    diffs = np.diff(time).astype("timedelta64[h]").astype(int)
    if diffs.size == 0:
        return "unknown"

    freq_hours = int(np.bincount(diffs).argmax())
    return f"{freq_hours}H"


# ------------------------------------------------------------------------------
# Missing timestamp detection
# ------------------------------------------------------------------------------


def detect_missing_timestamps(time: np.ndarray, freq_hours: int) -> list[str]:
    """Detect missing timestamps based on expected frequency."""
    missing: list[str] = []
    diffs = np.diff(time).astype("timedelta64[h]").astype(int)

    for i, d in enumerate(diffs):
        if d > freq_hours:
            gap_count = d // freq_hours - 1
            for g in range(gap_count):
                missing_ts = time[i] + np.timedelta64((g + 1) * freq_hours, "h")
                missing.append(str(missing_ts))

    return missing


# ------------------------------------------------------------------------------
# Build aligned timestamps
# ------------------------------------------------------------------------------


def build_aligned_time(time: np.ndarray, freq_hours: int) -> np.ndarray:
    """Build evenly spaced aligned timestamps with same length as original."""
    start = time[0]
    n = time.size

    aligned = start + np.arange(n) * np.timedelta64(freq_hours, "h")
    return aligned.astype("datetime64[ns]")


# ------------------------------------------------------------------------------
# Dataset expansion
# ------------------------------------------------------------------------------


def expand_dataset_to_aligned_time(
    ds: xr.Dataset,
    aligned_time: np.ndarray,
    fields: list[str],
) -> xr.Dataset:
    """
    Expand dataset to include missing timestamps.

    - New time axis = aligned_time
    - Existing slices preserved
    - Missing slices filled with NaN
    """

    ds_expanded = ds.reindex(time=aligned_time)

    # Ensure all fields exist and have correct shape
    for field in fields:
        if field not in ds_expanded:
            raise ValueError(f"[Stage 4][temporal_align] Missing field '{field}'")

    return ds_expanded


# ------------------------------------------------------------------------------
# Contract builder
# ------------------------------------------------------------------------------


def build_temporal_contract(
    aligned_time: np.ndarray,
    frequency: str,
    missing: list[str],
) -> Mapping[str, Any]:
    return {
        "aligned_time": aligned_time,
        "frequency": frequency,
        "missing_timestamps": missing,
    }


# ------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------


def process_temporal_alignment(ds: xr.Dataset, fields: list[str]):
    time = ds["time"].values

    # 1. Compute frequency
    diffs = np.diff(time.astype("datetime64[h]").astype(int))
    freq_hours = int(np.min(diffs))

    # 2. Build evenly spaced aligned_time (same length as original)
    aligned_time = build_aligned_time(time, freq_hours)

    # 3. Resample dataset to aligned_time
    ds_aligned = ds.interp(time=aligned_time)

    # 4. Detect missing timestamps (for metadata only)
    original_set = set(time.astype("datetime64[ns]"))
    missing = [str(t) for t in aligned_time if t not in original_set]

    contract = {
        "aligned_time": aligned_time,
        "frequency": f"{freq_hours}H",
        "missing_timestamps": missing,
    }

    print("[Stage 4][temporal_align] frequency:", f"{freq_hours}H")
    print("[Stage 4][temporal_align] missing:", len(missing))
    print("[Stage 4][temporal_align] aligned_time length:", aligned_time.size)

    return ds_aligned, contract
