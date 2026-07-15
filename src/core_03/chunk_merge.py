"""
Stage 3: Chunk Merger — Timestamp‑Aligned, Variable‑Safe (Single‑Variable Chunks)
=================================================================================

Purpose:
    Combine Stage‑3 chunk parquet outputs into a single spatiotemporal dataset
    suitable for Stage‑4 tensor construction.

Assumptions (Branch‑2, single‑variable mode):
    • each chunk parquet contains: time, lat, lon, <variable>
    • one variable per chunk (spec.variable)
    • no GRIB metadata columns
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import xarray as xr

# ------------------------------------------------------------------------------
# LOAD CHUNK OUTPUTS
# ------------------------------------------------------------------------------

def load_chunk_outputs(chunk_specs: List[Any], config: Dict[str, Any]) -> Dict[str, List[xr.Dataset]]:
    """
    Load Stage‑3 parquet chunk outputs and convert them into xarray datasets.

    Returns:
        Dict[var_name, List[xr.Dataset]] — datasets grouped by variable.
    """

    grouped: Dict[str, List[xr.Dataset]] = {}

    for spec in chunk_specs:
        parquet_path = Path(spec.output_path)
        if not parquet_path.exists():
            raise FileNotFoundError(f"Missing chunk output: {parquet_path}")

        df = pd.read_parquet(parquet_path)
        df = df.loc[:, ~df.columns.duplicated()]

        # Keep only coordinates + the variable present in the chunk
        cols = [c for c in df.columns if c in ["time", "lat", "lon"]]
        vars = [c for c in df.columns if c not in ["time", "lat", "lon"]]

        df = df[cols + vars]

        # Drop duplicate rows and ensure coordinate uniqueness
        df = df.drop_duplicates()
        df = df.drop_duplicates(subset=["time", "lat", "lon"])

        # Convert to xarray
        ds = df.set_index(["time", "lat", "lon"]).to_xarray()

        # Ensure unique time index
        _, unique_idx = np.unique(ds["time"], return_index=True)
        ds = ds.isel(time=unique_idx)

        var = spec.variable
        if var not in grouped:
            grouped[var] = []
        grouped[var].append(ds[[var]])

    return grouped


# ------------------------------------------------------------------------------
# MERGE DATASETS
# ------------------------------------------------------------------------------

def merge_datasets(grouped: Dict[str, List[xr.Dataset]]) -> xr.Dataset:
    """
    Merge grouped variable datasets into a unified spatiotemporal dataset.
    """

    if not grouped:
        raise ValueError("No chunk datasets to merge")

    per_var: Dict[str, xr.Dataset] = {}

    # 1. Concat per variable
    for v, dsv in grouped.items():
        ds_v = xr.concat(dsv, dim="time").sortby("time")
        _, unique_idx = np.unique(ds_v["time"], return_index=True)
        ds_v = ds_v.isel(time=unique_idx)
        per_var[v] = ds_v

    # 2. Compute union of timestamps
    all_times = [set(ds_v.time.values) for ds_v in per_var.values()]
    full_time = sorted(set.union(*all_times))

    # 3. Reindex each variable to full timeline
    for v in per_var:
        per_var[v] = per_var[v].reindex(time=full_time)

    # 4. Merge aligned variables
    ds_merged = xr.merge(list(per_var.values()))

    return ds_merged


# ------------------------------------------------------------------------------
# METADATA + QC
# ------------------------------------------------------------------------------

def build_merged_metadata(ds: xr.Dataset) -> Dict[str, Any]:
    return {
        "n_time": ds.sizes["time"],
        "n_lat": ds.sizes["lat"],
        "n_lon": ds.sizes["lon"],
        "variables": list(ds.data_vars.keys()),
        "coords": list(ds.coords.keys()),
    }


def build_merged_qc(ds: xr.Dataset) -> Dict[str, Any]:
    qc = {}
    for var in ds.data_vars:
        qc[var] = {
            "nan_count": int(ds[var].isnull().sum().values),
            "min": float(ds[var].min().values),
            "max": float(ds[var].max().values),
        }
    return qc


# ------------------------------------------------------------------------------
# WRITE OUTPUTS
# ------------------------------------------------------------------------------

def write_outputs(
    ds: xr.Dataset,
    metadata: Dict[str, Any],
    qc: Dict[str, Any],
    config: Dict[str, Any],
) -> None:
    merged_nc = Path(config["paths"]["stage3_merged"])
    merged_meta = Path(config["paths"]["stage3_metadata"])
    merged_qc = Path(config["paths"]["stage3_qc"])

    merged_nc.parent.mkdir(parents=True, exist_ok=True)

    ds.to_netcdf(merged_nc)

    with open(merged_meta, "w") as f:
        json.dump(metadata, f, indent=2)

    with open(merged_qc, "w") as f:
        json.dump(qc, f, indent=2)


# ------------------------------------------------------------------------------
# HIGH-LEVEL MERGE ENTRYPOINT
# ------------------------------------------------------------------------------

def merge_chunks(chunk_specs: List[Any], config: Dict[str, Any]) -> xr.Dataset:
    grouped = load_chunk_outputs(chunk_specs, config)
    ds_merged = merge_datasets(grouped)

    metadata = build_merged_metadata(ds_merged)
    qc = build_merged_qc(ds_merged)

    write_outputs(ds_merged, metadata, qc, config)

    return ds_merged
