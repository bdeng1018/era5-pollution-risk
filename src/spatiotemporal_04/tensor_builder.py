"""
Stage 4 – Tensor Builder Invariant
==================================

Purpose
-------
Assemble the canonical Stage 4 tensor (time × lat × lon × variables)
using validated spatial, temporal, and mask contracts.

Responsibilities
----------------
- Validate shape consistency across contracts
- Apply spatial mask to tensor arrays
- Construct canonical tensor dataset
- Do NOT modify spatial or temporal structure
"""

from collections.abc import Mapping
from typing import Any

import numpy as np
import xarray as xr

# ------------------------------------------------------------------------------
# Tensor construction
# ------------------------------------------------------------------------------


def build_tensor_dataset(
    ds_interpolated: xr.Dataset,
    grid_contract: Mapping[str, Any],
    temporal_contract: Mapping[str, Any],
    mask_contract: Mapping[str, Any],
    fields: list[str],
) -> xr.Dataset:
    """
    Construct canonical Stage 4 tensor dataset using real interpolated data.
    """

    lat = np.asarray(grid_contract["lat"])
    lon = np.asarray(grid_contract["lon"])
    time = np.asarray(temporal_contract["aligned_time"])
    mask = np.asarray(mask_contract["mask"])

    assert mask.shape == (
        lat.size,
        lon.size,
    ), "[Stage 4][tensor_builder] mask shape mismatch"

    ds = xr.Dataset(coords={"time": time, "lat": lat, "lon": lon})

    for field in fields:
        arr = ds_interpolated[field].values.copy()

        # -------------------------
        # Normalization rules
        # -------------------------

        # Temperature: Celsius → Kelvin
        if field == "t2m":
            arr = arr + 273.15

        # Dewpoint: Celsius → Kelvin (ERA5 d2m is Kelvin already, but safe)
        if field == "d2m":
            arr = arr  # no change needed

        # Cloud cover: 0–100 → 0–1
        if field == "tcc":
            arr = arr / 100.0
            arr[arr < 0] = 0.0  # fix tiny negative floats

        # Pressure: Pa → hPa
        if field in ("msl", "sp"):
            arr = arr / 100.0

        # Boundary layer height: clip extreme spikes
        if field == "blh":
            arr = np.clip(arr, 0, 5000)

        # CAPE/CIN: clip extreme spikes
        if field == "cape":
            arr = np.clip(arr, 0, 6000)

        if field == "cin":
            arr = np.clip(arr, 0, 1000)

        # -------------------------
        # Apply spatial mask
        # -------------------------
        mask3d = np.broadcast_to(mask, arr.shape)
        arr = np.where(mask3d, arr, np.nan)

        ds[field] = (("time", "lat", "lon"), arr)

    ds["mask"] = (("lat", "lon"), mask)

    return ds


# ------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------


def process_spatiotemporal_merge(
    ds_interpolated: xr.Dataset,
    grid_contract: Mapping[str, Any],
    mask_contract: Mapping[str, Any],
    temporal_contract: Mapping[str, Any],
    fields: list[str],
) -> xr.Dataset:
    """
    Stage 4 tensor builder invariant entry point.
    """

    ds = build_tensor_dataset(
        ds_interpolated=ds_interpolated,
        grid_contract=grid_contract,
        temporal_contract=temporal_contract,
        mask_contract=mask_contract,
        fields=fields,
    )

    print("[Stage 4][tensor_builder] tensor shape:", ds.to_array().shape)
    return ds
