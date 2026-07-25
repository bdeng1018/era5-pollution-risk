"""
Stage 4 – Temporal Interpolation Invariant
==========================================

Responsibilities:
- Interpolate values along the time dimension only
- Fill NaNs at timestamps introduced by temporal alignment
- Produce a deterministic interpolation contract
- Do NOT modify spatial structure
- Do NOT modify lat/lon resolution
"""

from collections.abc import Mapping
from typing import Any

import numpy as np
import xarray as xr

# ------------------------------------------------------------------------------
# Core interpolation
# ------------------------------------------------------------------------------


def interpolate_time(ds: xr.Dataset, fields: list[str]) -> xr.Dataset:
    """
    Interpolate values along the time dimension only.
    Assumes time is evenly spaced (from temporal_align).
    """

    ds_interp = ds.copy()

    for field in fields:
        if field not in ds_interp:
            raise ValueError(f"[Stage 4][temporal_interp] Missing field '{field}'")

        # Interpolate along time dimension
        ds_interp[field] = ds[field].interp(
            time=ds["time"],
            method="linear",
        )

    return ds_interp


# ------------------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------------------


def detect_added_timestamps(
    original_time: np.ndarray, aligned_time: np.ndarray
) -> list[str]:
    """
    Identify timestamps that were added during temporal alignment.
    """

    original_set = set(original_time.astype("datetime64[ns]"))
    added = [
        str(t) for t in aligned_time.astype("datetime64[ns]") if t not in original_set
    ]
    return added


def compute_interpolated_fraction(
    ds_before: xr.Dataset,
    ds_after: xr.Dataset,
    fields: list[str],
) -> float:
    """
    Fraction of values that were interpolated (i.e., changed from NaN to non-NaN).
    """

    before_count = 0
    after_count = 0

    for field in fields:
        before_arr = ds_before[field].values
        after_arr = ds_after[field].values

        before_count += np.isnan(before_arr).sum()
        after_count += np.isnan(after_arr).sum()

    if before_count == 0:
        return 0.0

    return float((before_count - after_count) / before_count)


# ------------------------------------------------------------------------------
# Contract builder
# ------------------------------------------------------------------------------


def build_interpolation_contract(
    method: str,
    added_timestamps: list[str],
    interpolated_fraction: float,
    original_time: np.ndarray,
    aligned_time: np.ndarray,
    filled_indices: list[int],
) -> Mapping[str, Any]:
    """
    Construct Stage 4 temporal interpolation metadata contract.
    """

    return {
        "method": method,
        "added_timestamps": added_timestamps,
        "interpolated_fraction": interpolated_fraction,
        "attrs": {
            "original_time": original_time.astype("datetime64[ns]").tolist(),
            "aligned_time": aligned_time.astype("datetime64[ns]").tolist(),
            "interpolated_time": aligned_time.astype("datetime64[ns]").tolist(),
            "filled_indices": filled_indices,
        },
    }


# ------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------


def process_interpolation(
    ds: xr.Dataset,
    fields: list[str],
) -> tuple[xr.Dataset, Mapping[str, Any]]:

    original_time = ds["time"].values

    # 1. Interpolate along time dimension
    ds_interp = interpolate_time(ds, fields)

    # 2. Detect added timestamps
    aligned_time = ds_interp["time"].values
    added_ts = detect_added_timestamps(original_time, aligned_time)

    # 3. Compute interpolation fraction
    frac = compute_interpolated_fraction(ds, ds_interp, fields)

    # 4. Compute filled indices (timestamps where interpolation occurred)
    filled_indices = []
    for i, t in enumerate(aligned_time):
        if t not in original_time:
            filled_indices.append(i)

    # 5. Build full contract (UPDATED)
    contract = build_interpolation_contract(
        method="linear",
        added_timestamps=added_ts,
        interpolated_fraction=frac,
        original_time=original_time,
        aligned_time=aligned_time,
        filled_indices=filled_indices,
    )

    # Preserve original_time in attrs for diagnostics
    ds_interp.attrs["original_time"] = original_time

    print("[Stage 4][temporal_interp] added_timestamps:", len(added_ts))
    print("[Stage 4][temporal_interp] interpolated_fraction:", frac)

    return ds_interp, contract
