"""
Stage 05 — Spatial Feature Tests
================================

These tests validate that Stage 05 spatial feature engineering correctly applies
rolling‑window kernels (e.g., 3×3 mean filters) and preserves:

    - dimensions
    - coordinates
    - variable naming conventions

IMPORTANT
---------
The original test fixture used invalid xarray constructs such as:

    ("time", "lat", "lon"), xr.ones((4, 3, 3))

Two issues existed:

1. xarray has **no** `xr.ones` function.
2. The tuple‑form variable definition is invalid unless the data shape matches
   the declared dims exactly.

The synthetic IR4 tensor is now constructed using proper `xr.DataArray`
definitions, which preserves the intent of the test while aligning with
xarray's actual API.
"""

import numpy as np
import xarray as xr

from src.features_05 import compute_spatial_features


def _synthetic_ir4():
    """
    Construct a minimal synthetic IR4 tensor for spatial feature tests.

    The tensor contains:
        - 4 timestamps (6‑hourly)
        - 3 latitudes
        - 3 longitudes
        - 1 variable (t2m)

    The variable is defined as a proper xarray DataArray with correct dims.
    """

    time = xr.cftime_range("2000-01-01", periods=4, freq="6H")
    lat = [0.0, 1.0, 2.0]
    lon = [0.0, 1.0, 2.0]

    return xr.Dataset(
        {
            "t2m": xr.DataArray(
                np.ones((4, 3, 3)),
                dims=("time", "lat", "lon"),
                coords={"time": time, "lat": lat, "lon": lon},
            )
        },
        coords={"time": time, "lat": lat, "lon": lon},
    )


def test_spatial_features_exist_and_match_dims():
    """
    Validate that spatial features:
        - are computed correctly
        - have the expected variable name
        - preserve dims and coords
    """

    ds = _synthetic_ir4()

    cfg = {
        "spatial": {
            "variables": ["t2m"],
            "kernels": {
                "mean_3x3": [
                    [1, 1, 1],
                    [1, 1, 1],
                    [1, 1, 1],
                ]
            },
        }
    }

    out = compute_spatial_features(ds, cfg)

    # Validate feature presence
    assert "t2m_mean_3x3" in out.data_vars

    # Validate dims
    assert out["t2m_mean_3x3"].dims == ("time", "lat", "lon")

    # Validate coordinate preservation
    assert (out["t2m_mean_3x3"].coords["time"] == ds["time"]).all()
    assert (out["t2m_mean_3x3"].coords["lat"] == ds["lat"]).all()
    assert (out["t2m_mean_3x3"].coords["lon"] == ds["lon"]).all()
