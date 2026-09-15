"""
Stage 05 — Smoke Test
=====================

This smoke test validates that Stage 05 can run end‑to‑end on a tiny synthetic
IR4 tensor and produce:

    - stage5_features.nc
    - stage5_metadata.json
    - stage5_qc.json

IMPORTANT
---------
The original test fixture used invalid xarray constructs such as:

    xr.ones((4, 2, 2))

Two issues existed:

1. xarray has **no** `xr.ones` function.
2. The tuple‑form variable definition is invalid unless the data shape matches
   the declared dims exactly.

The synthetic IR4 tensor is now constructed using proper `xr.DataArray`
definitions, which preserves the intent of the smoke test while aligning with
xarray's actual API.
"""

import numpy as np
import xarray as xr

from src.features_05 import run_stage05


def test_stage05_smoke(tmp_path, monkeypatch):
    """
    Smoke test: run Stage 05 on a tiny synthetic tensor and ensure it completes
    without raising exceptions.

    This test does not validate numerical correctness — only that the pipeline
    executes successfully and produces the expected output files.
    """

    # Proper synthetic IR4 tensor using valid xarray DataArray construction.
    ds = xr.Dataset(
        {
            "t2m": xr.DataArray(
                280.0 * np.ones((4, 2, 2)),
                dims=("time", "lat", "lon"),
                coords={
                    "time": xr.cftime_range("2000-01-01", periods=4, freq="6H"),
                    "lat": [0.0, 1.0],
                    "lon": [0.0, 1.0],
                },
            ),
            "d2m": xr.DataArray(
                275.0 * np.ones((4, 2, 2)),
                dims=("time", "lat", "lon"),
                coords={
                    "time": xr.cftime_range("2000-01-01", periods=4, freq="6H"),
                    "lat": [0.0, 1.0],
                    "lon": [0.0, 1.0],
                },
            ),
            "u10": xr.DataArray(
                np.ones((4, 2, 2)),
                dims=("time", "lat", "lon"),
                coords={
                    "time": xr.cftime_range("2000-01-01", periods=4, freq="6H"),
                    "lat": [0.0, 1.0],
                    "lon": [0.0, 1.0],
                },
            ),
            "v10": xr.DataArray(
                np.ones((4, 2, 2)),
                dims=("time", "lat", "lon"),
                coords={
                    "time": xr.cftime_range("2000-01-01", periods=4, freq="6H"),
                    "lat": [0.0, 1.0],
                    "lon": [0.0, 1.0],
                },
            ),
            "msl": xr.DataArray(
                101325.0 * np.ones((4, 2, 2)),
                dims=("time", "lat", "lon"),
                coords={
                    "time": xr.cftime_range("2000-01-01", periods=4, freq="6H"),
                    "lat": [0.0, 1.0],
                    "lon": [0.0, 1.0],
                },
            ),
        }
    )

    # Write synthetic IR4 tensor to disk
    ir4_path = tmp_path / "stage4_tensor.nc"
    ds.to_netcdf(ir4_path)

    # Minimal Stage 05 configuration — updated to match Stage 05 implementation
    cfg = {
        "ir4": {"version": "5.0-features"},
        "paths": {
            "input": str(ir4_path),
            "output": str(tmp_path / "stage5_features.nc"),
            "metadata": str(tmp_path / "stage5_metadata.json"),
            "qc": str(tmp_path / "stage5_qc.json"),
        },
        "temporal": {
            "variables": ["t2m"],
            "window_6h": 6,
            "window_24h": 24,
        },
        "spatial": {
            "variables": ["t2m"],
            "kernels": {
                # Minimal kernel to ensure spatial features exist
                "mean_3x3": [
                    [1, 1, 1],
                    [1, 1, 1],
                    [1, 1, 1],
                ]
            },
        },
        "composites": {
            # Minimal composite to ensure composite layer exists
            "simple_index": {
                "temporal": ["t2m_roll_mean_6h"],
                "spatial": ["t2m_mean_3x3"],
                "formula": "t2m_roll_mean_6h + t2m_mean_3x3",
            }
        },
        "registry": {
            "temporal": ["t2m_roll_mean_6h", "t2m_delta_24h"],
            "spatial": ["t2m_mean_3x3"],
            "composite": ["simple_index"],
        },
    }

    # Run Stage 05 directly (no CLI)
    run_stage05(cfg)

    # Validate output artifacts
    assert (tmp_path / "stage5_features.nc").exists()
    assert (tmp_path / "stage5_metadata.json").exists()
    assert (tmp_path / "stage5_qc.json").exists()
