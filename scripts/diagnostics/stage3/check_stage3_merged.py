"""
Stage 3 Diagnostics — Comprehensive Analysis of Merged Outputs
==============================================================

Analyzes:
    • merged.nc
    • merged_metadata.json
    • merged_qc.json

Outputs:
    • NaN counts and percentages per variable
    • Coordinate integrity checks
    • Timestamp coverage
    • Spatial grid consistency
    • QC summary
    • Metadata summary
    • Dataset shape and memory footprint
    • Dtype summary
"""

import json
from pathlib import Path

import numpy as np
import xarray as xr


def analyze_stage3_outputs(base_dir="data/intermediate"):
    base = Path(base_dir)

    merged_nc = base / "merged.nc"
    merged_meta = base / "merged_metadata.json"
    merged_qc = base / "merged_qc.json"

    print("\n=== Stage 3 Diagnostics ===\n")

    # --------------------------------------------------------------------------
    # Load merged.nc
    # --------------------------------------------------------------------------
    print("Loading merged.nc ...")
    ds = xr.open_dataset(merged_nc)

    print("\nDataset summary:")
    print(ds)

    print("\nDimensions:")
    for dim, size in ds.dims.items():
        print(f"  {dim}: {size}")

    print("\nVariables:")
    for var in ds.data_vars:
        print(f"  {var}: {ds[var].dtype}")

    # --------------------------------------------------------------------------
    # NaN analysis
    # --------------------------------------------------------------------------
    print("\n=== NaN Analysis ===")
    nan_report = {}

    for var in ds.data_vars:
        arr = ds[var].values
        total = arr.size
        n_nan = np.isnan(arr).sum()
        pct_nan = (n_nan / total) * 100

        nan_report[var] = {
            "total_values": int(total),
            "nan_count": int(n_nan),
            "nan_pct": float(pct_nan),
        }

        print(f"{var}: {n_nan} NaN ({pct_nan:.4f}%)")

    # --------------------------------------------------------------------------
    # Timestamp coverage per variable
    # --------------------------------------------------------------------------
    print("\n=== Timestamp Coverage per Variable ===")
    ts_report = {}

    for var in ds.data_vars:
        valid_time = ds[var].dropna("time")
        ts_report[var] = {
            "valid_timestamps": int(valid_time.sizes.get("time", 0)),
            "total_timestamps": int(ds.sizes["time"]),
        }
        print(f"{var}: {valid_time.sizes.get('time', 0)} / {ds.sizes['time']} valid")

    # --------------------------------------------------------------------------
    # Spatial coverage per variable
    # --------------------------------------------------------------------------
    print("\n=== Spatial Coverage per Variable ===")
    spatial_report = {}

    for var in ds.data_vars:
        valid_lat = ds[var].dropna("lat")
        valid_lon = ds[var].dropna("lon")
        spatial_report[var] = {
            "valid_lat": int(valid_lat.sizes.get("lat", 0)),
            "valid_lon": int(valid_lon.sizes.get("lon", 0)),
            "total_lat": int(ds.sizes["lat"]),
            "total_lon": int(ds.sizes["lon"]),
        }
        print(
            f"{var}: lat {valid_lat.sizes.get('lat', 0)}/{ds.sizes['lat']}, "
            f"lon {valid_lon.sizes.get('lon', 0)}/{ds.sizes['lon']}"
        )

    # --------------------------------------------------------------------------
    # NaN distribution by time (detect timestamp misalignment)
    # --------------------------------------------------------------------------
    print("\n=== NaN Distribution by Time (First 20 timestamps) ===")
    nan_time_report = {}

    for var in ds.data_vars:
        arr = ds[var].values
        nan_by_time = np.isnan(arr).sum(axis=(1, 2))
        nan_time_report[var] = nan_by_time.tolist()
        print(f"{var}: {nan_by_time[:20]}")

    # --------------------------------------------------------------------------
    # Coordinate integrity
    # --------------------------------------------------------------------------
    print("\n=== Coordinate Integrity ===")
    print("Time range:")
    print(f"  start: {ds['time'].min().values}")
    print(f"  end:   {ds['time'].max().values}")
    print(f"  count: {ds['time'].size}")

    print("\nLatitude range:")
    print(f"  min: {ds['lat'].min().values}")
    print(f"  max: {ds['lat'].max().values}")
    print(f"  count: {ds['lat'].size}")

    print("\nLongitude range:")
    print(f"  min: {ds['lon'].min().values}")
    print(f"  max: {ds['lon'].max().values}")
    print(f"  count: {ds['lon'].size}")

    # --------------------------------------------------------------------------
    # Metadata JSON
    # --------------------------------------------------------------------------
    print("\n=== Metadata JSON ===")
    with open(merged_meta, "r") as f:
        meta = json.load(f)

    print(json.dumps(meta, indent=2))

    # --------------------------------------------------------------------------
    # QC JSON
    # --------------------------------------------------------------------------
    print("\n=== QC JSON ===")
    with open(merged_qc, "r") as f:
        qc = json.load(f)

    print(json.dumps(qc, indent=2))

    # --------------------------------------------------------------------------
    # Memory footprint
    # --------------------------------------------------------------------------
    print("\n=== Memory Footprint ===")
    print(ds.nbytes, "bytes")

    print("\nDiagnostics complete.\n")


if __name__ == "__main__":
    analyze_stage3_outputs()
