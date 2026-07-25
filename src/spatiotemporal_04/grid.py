"""
Stage 4 – Grid Invariant
========================

Purpose
-------
Normalize and validate the spatial coordinate system for Stage 4.
This invariant ensures that downstream operations (masking, temporal
alignment, interpolation, tensor assembly, QC) operate on a consistent,
reproducible spatial grid.

Responsibilities
----------------
- Validate presence of 'lat' and 'lon' coordinates
- Ensure latitude is strictly ascending
- Normalize longitude into [-180, 180] range
- Ensure longitude is strictly ascending
- Detect irregular spacing or duplicate coordinates
- Produce a deterministic spatial metadata contract
- Do NOT modify spatial resolution or slice structure

Outputs
-------
Returns:
    (normalized_dataset, spatial_contract)

Where spatial_contract contains:
    {
        "lat": np.ndarray,
        "lon": np.ndarray,
        "crs": "EPSG:4326",
        "lat_ascending": bool,
        "lon_ascending": bool,
        "lat_spacing": float,
        "lon_spacing": float,
        "warnings": list[str],
    }
"""

from collections.abc import Mapping

import numpy as np
import xarray as xr

# ------------------------------------------------------------------------------
# Utility checks
# ------------------------------------------------------------------------------


def _assert_coordinate_exists(ds: xr.Dataset, name: str) -> None:
    if name not in ds.coords:
        raise ValueError(f"[Stage 4][grid] Missing coordinate '{name}'")


def _is_strictly_ascending(arr: np.ndarray) -> bool:
    """Return True if array is strictly ascending."""
    return bool(np.all(np.diff(arr) > 0))  # <-- FIX: cast numpy.bool_ → bool


def _compute_spacing(arr: np.ndarray) -> float:
    diffs = np.diff(arr)
    return float(np.median(diffs)) if diffs.size > 0 else float("nan")


def _detect_spacing_irregularity(arr: np.ndarray) -> bool:
    diffs = np.diff(arr)
    if diffs.size == 0:
        return False
    return bool(np.std(diffs) > 1e-6)  # <-- FIX: cast numpy.bool_ → bool


# ------------------------------------------------------------------------------
# Normalization
# ------------------------------------------------------------------------------


def normalize_lat_lon(ds: xr.Dataset) -> xr.Dataset:
    ds_norm = ds.copy()

    # --- Latitude ---
    lat = ds_norm["lat"].values
    if not _is_strictly_ascending(lat):
        ds_norm = ds_norm.sortby("lat")

    # --- Longitude ---
    lon = ds_norm["lon"].values
    lon_norm = ((lon + 180) % 360) - 180
    ds_norm = ds_norm.assign_coords(lon=("lon", lon_norm))

    lon2 = ds_norm["lon"].values
    if not _is_strictly_ascending(lon2):
        ds_norm = ds_norm.sortby("lon")

    return ds_norm


# ------------------------------------------------------------------------------
# Contract builder
# ------------------------------------------------------------------------------


def build_spatial_contract(
    ds: xr.Dataset,
) -> Mapping[str, np.ndarray | str | float | list[str]]:
    lat = ds["lat"].values
    lon = ds["lon"].values

    warnings: list[str] = []

    lat_spacing = _compute_spacing(lat)
    lon_spacing = _compute_spacing(lon)

    if _detect_spacing_irregularity(lat):
        warnings.append("irregular_lat_spacing")

    if _detect_spacing_irregularity(lon):
        warnings.append("irregular_lon_spacing")

    return {
        "lat": lat,
        "lon": lon,
        "crs": "EPSG:4326",
        "lat_ascending": _is_strictly_ascending(lat),
        "lon_ascending": _is_strictly_ascending(lon),
        "lat_spacing": lat_spacing,
        "lon_spacing": lon_spacing,
        "warnings": warnings,
    }


# ------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------


def process_grid(
    ds: xr.Dataset,
) -> tuple[xr.Dataset, Mapping[str, np.ndarray | str | float | list[str]]]:
    _assert_coordinate_exists(ds, "lat")
    _assert_coordinate_exists(ds, "lon")

    ds_norm = normalize_lat_lon(ds)
    contract = build_spatial_contract(ds_norm)

    # Logging hook (safe extraction)
    lat_arr = np.asarray(contract["lat"])
    lon_arr = np.asarray(contract["lon"])

    lat_min = float(lat_arr.min())
    lat_max = float(lat_arr.max())
    lon_min = float(lon_arr.min())
    lon_max = float(lon_arr.max())

    print(f"[Stage 4][grid] lat range: {lat_min} → {lat_max}")
    print(f"[Stage 4][grid] lon range: {lon_min} → {lon_max}")

    if contract["warnings"]:
        print("[Stage 4][grid] warnings:", contract["warnings"])

    return ds_norm, contract
