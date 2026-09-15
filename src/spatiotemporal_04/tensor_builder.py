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

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr

# Deterministic artifact hashing (C++ boundary module)
from boundary_hash import sha256_file

# ==============================================================================
# Tensor construction
# ==============================================================================


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

        if field == "t2m":  # Celsius → Kelvin
            arr = arr + 273.15

        if field == "d2m":  # ERA5 d2m is already Kelvin
            arr = arr

        if field == "tcc":  # 0–100 → 0–1
            arr = arr / 100.0
            arr[arr < 0] = 0.0

        if field in ("msl", "sp"):  # Pa → hPa
            arr = arr / 100.0

        if field == "blh":  # Clip extreme spikes
            arr = np.clip(arr, 0, 5000)

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


# ==============================================================================
# Metadata + QC
# ==============================================================================


def build_tensor_metadata(ds: xr.Dataset) -> dict[str, Any]:
    return {
        "n_time": ds.sizes["time"],
        "n_lat": ds.sizes["lat"],
        "n_lon": ds.sizes["lon"],
        "variables": list(ds.data_vars.keys()),
        "coords": list(ds.coords.keys()),
    }


def build_tensor_qc(ds: xr.Dataset) -> dict[str, Any]:
    qc = {}
    for var in ds.data_vars:
        qc[var] = {
            "nan_count": int(ds[var].isnull().sum().values),
            "min": float(ds[var].min().values),
            "max": float(ds[var].max().values),
        }
    return qc


# ==============================================================================
# Write outputs + deterministic hashing
# ==============================================================================


def write_tensor_outputs(
    ds: xr.Dataset,
    metadata: dict[str, Any],
    qc: dict[str, Any],
    output_dir: Path,
) -> None:

    output_dir.mkdir(parents=True, exist_ok=True)

    tensor_nc = output_dir / "tensor_stage4.nc"
    tensor_meta = output_dir / "tensor_metadata.json"
    tensor_qc = output_dir / "tensor_qc.json"

    # Write NetCDF
    ds.to_netcdf(tensor_nc)
    digest_nc = sha256_file(str(tensor_nc))

    # Write metadata.json
    tensor_meta.write_text(json.dumps(metadata, indent=2))
    digest_meta = sha256_file(str(tensor_meta))

    # Write qc.json
    tensor_qc.write_text(json.dumps(qc, indent=2))
    digest_qc = sha256_file(str(tensor_qc))

    print(
        f"[Stage 4] SHA256 digests:\n"
        f"  tensor_stage4.nc   → {digest_nc}\n"
        f"  tensor_metadata.json → {digest_meta}\n"
        f"  tensor_qc.json       → {digest_qc}"
    )


# ==============================================================================
# Entry point
# ==============================================================================


def process_spatiotemporal_merge(
    ds_interpolated: xr.Dataset,
    grid_contract: Mapping[str, Any],
    mask_contract: Mapping[str, Any],
    temporal_contract: Mapping[str, Any],
    fields: list[str] | None = None,
    output_dir: Path | None = None,
) -> xr.Dataset:
    """
    Stage 4 tensor builder invariant entry point.

    Tests call this function with 4, 5, or 6 arguments.
    To preserve deterministic behavior while remaining test‑compatible,
    `fields` and `output_dir` are optional:

        • fields: defaults to all variables in ds_interpolated
        • output_dir: defaults to a temporary directory under ./stage4_output/

    No spatial or temporal structure is modified.
    """

    # Default fields: all interpolated variables
    if fields is None:
        fields = list(ds_interpolated.data_vars.keys())

    # Default output directory
    if output_dir is None:
        output_dir = Path("stage4_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    ds = build_tensor_dataset(
        ds_interpolated=ds_interpolated,
        grid_contract=grid_contract,
        temporal_contract=temporal_contract,
        mask_contract=mask_contract,
        fields=fields,
    )

    print("[Stage 4][tensor_builder] tensor shape:", ds.to_array().shape)

    metadata = build_tensor_metadata(ds)
    qc = build_tensor_qc(ds)

    write_tensor_outputs(ds, metadata, qc, output_dir)

    return ds
