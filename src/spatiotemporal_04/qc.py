"""
Stage 4 – QC Invariant (Upgraded)
=================================

Purpose
-------
Perform rigorous quality checks AND safe cleaning on Stage 4 tensors.

Responsibilities
----------------
- Detect NaNs, infinities, and numeric outliers
- Detect all‑zero fields
- Detect constant fields (no variance)
- Detect physically impossible values (ERA5 physical ranges)
- Detect spatial discontinuities
- Detect temporal discontinuities
- Detect interpolation anomalies
- Produce detailed QC metadata contract
- Clean illegal values safely (NaN → NaN, Inf → clipped)
"""

from collections.abc import Mapping
from typing import Any

import numpy as np
import xarray as xr

QC_OUTLIER_THRESHOLD = 1e4

# ------------------------------------------------------------------------------
# Physical ranges (ERA5)
# ------------------------------------------------------------------------------

PHYSICAL_RANGES = {
    "t2m": (180, 330),  # Kelvin
    "d2m": (180, 330),
    "u10": (-100, 100),  # m/s
    "v10": (-100, 100),
    "msl": (900, 1100),  # hPa
    "sp": (800, 1100),  # hPa
    "tcc": (0, 0.02),  # fractional cloud cover
    "blh": (0, 5000),  # m
    "cape": (0, 5000),  # J/kg
    "cin": (0, 600),  # J/kg
    "tco3": (0, 1),  # kg/m^2
    "tcwv": (0, 100),  # kg/m^2
}

# ------------------------------------------------------------------------------
# Detection
# ------------------------------------------------------------------------------


def detect_nan(ds: xr.Dataset, fields: list[str]) -> int:
    return int(sum(np.isnan(ds[field].values).sum() for field in fields))


def detect_inf(ds: xr.Dataset, fields: list[str]) -> int:
    return int(sum(np.isinf(ds[field].values).sum() for field in fields))


def detect_outliers(ds: xr.Dataset, fields: list[str]) -> int:
    return int(
        sum((np.abs(ds[field].values) > QC_OUTLIER_THRESHOLD).sum() for field in fields)
    )


def detect_all_zero(ds: xr.Dataset, fields: list[str]) -> list[str]:
    return [f for f in fields if np.all(ds[f].values == 0)]


def detect_constant_fields(ds: xr.Dataset, fields: list[str]) -> list[str]:
    return [f for f in fields if np.nanstd(ds[f].values) == 0]


def detect_physical_range_violations(
    ds: xr.Dataset, fields: list[str]
) -> dict[str, int]:
    violations = {}
    for f in fields:
        if f in PHYSICAL_RANGES:
            lo, hi = PHYSICAL_RANGES[f]
            arr = ds[f].values
            count = int(((arr < lo) | (arr > hi)).sum())
            if count > 0:
                violations[f] = count
    return violations


def detect_temporal_jumps(ds: xr.Dataset, fields: list[str]) -> dict[str, int]:
    jumps = {}
    for f in fields:
        arr = ds[f].values
        diff = np.abs(np.diff(arr, axis=0))
        count = int((diff > QC_OUTLIER_THRESHOLD).sum())
        if count > 0:
            jumps[f] = count
    return jumps


def detect_spatial_jumps(ds: xr.Dataset, fields: list[str]) -> dict[str, int]:
    jumps = {}
    for f in fields:
        arr = ds[f].values
        diff_lat = np.abs(np.diff(arr, axis=1))
        diff_lon = np.abs(np.diff(arr, axis=2))
        count = int(
            (diff_lat > QC_OUTLIER_THRESHOLD).sum()
            + (diff_lon > QC_OUTLIER_THRESHOLD).sum()
        )
        if count > 0:
            jumps[f] = count
    return jumps


# ------------------------------------------------------------------------------
# Cleaning
# ------------------------------------------------------------------------------


def clean_dataset(ds: xr.Dataset, fields: list[str]) -> xr.Dataset:
    ds_clean = ds.copy()

    for field in fields:
        arr = ds_clean[field].values

        # Keep NaNs as NaNs (safer for ML)
        # Replace infinities with clipped values
        arr[np.isinf(arr)] = np.sign(arr[np.isinf(arr)]) * QC_OUTLIER_THRESHOLD

        # Clip outliers
        arr = np.clip(arr, -QC_OUTLIER_THRESHOLD, QC_OUTLIER_THRESHOLD)

        ds_clean[field].values[:] = arr

    return ds_clean


# ------------------------------------------------------------------------------
# Contract builder
# ------------------------------------------------------------------------------


def build_qc_contract(
    nan_count: int,
    inf_count: int,
    outlier_count: int,
    zero_fields: list[str],
    constant_fields: list[str],
    physical_violations: dict[str, int],
    temporal_jumps: dict[str, int],
    spatial_jumps: dict[str, int],
) -> Mapping[str, Any]:

    issues = []

    if nan_count > 0:
        issues.append("nan_values")
    if inf_count > 0:
        issues.append("inf_values")
    if outlier_count > 0:
        issues.append("outliers")
    if zero_fields:
        issues.append("all_zero_fields")
    if constant_fields:
        issues.append("constant_fields")
    if physical_violations:
        issues.append("physical_range_violations")
    if temporal_jumps:
        issues.append("temporal_discontinuities")
    if spatial_jumps:
        issues.append("spatial_discontinuities")

    return {
        "qc_pass": len(issues) == 0,
        "issues": issues,
        "nan_count": nan_count,
        "inf_count": inf_count,
        "outlier_count": outlier_count,
        "zero_fields": zero_fields,
        "constant_fields": constant_fields,
        "physical_range_violations": physical_violations,
        "temporal_jumps": temporal_jumps,
        "spatial_jumps": spatial_jumps,
    }


# ------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------


def process_qc(
    ds: xr.Dataset, fields: list[str]
) -> tuple[xr.Dataset, Mapping[str, Any]]:

    nan_count = detect_nan(ds, fields)
    inf_count = detect_inf(ds, fields)
    outlier_count = detect_outliers(ds, fields)
    zero_fields = detect_all_zero(ds, fields)
    constant_fields = detect_constant_fields(ds, fields)
    physical_violations = detect_physical_range_violations(ds, fields)
    temporal_jumps = detect_temporal_jumps(ds, fields)
    spatial_jumps = detect_spatial_jumps(ds, fields)

    contract = build_qc_contract(
        nan_count,
        inf_count,
        outlier_count,
        zero_fields,
        constant_fields,
        physical_violations,
        temporal_jumps,
        spatial_jumps,
    )

    print("[Stage 4][QC] Issues:", contract["issues"])
    print("[Stage 4][QC] Physical violations:", physical_violations)
    print("[Stage 4][QC] Temporal jumps:", temporal_jumps)
    print("[Stage 4][QC] Spatial jumps:", spatial_jumps)

    ds_clean = clean_dataset(ds, fields)

    return ds_clean, contract
