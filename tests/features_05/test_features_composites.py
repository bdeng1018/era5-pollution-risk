"""
Stage 05 — Composite Feature Tests
==================================

These tests validate that composite formulas defined in Stage 05 configuration
are evaluated correctly using temporal and spatial IR5 features.

IMPORTANT
---------
The original test fixture used invalid xarray constructs such as:

    ("time", "lat", "lon"), [0.0, 1.0, 2.0, 3.0]

This is not valid xarray syntax because the number of dimensions does not match
the number of data dimensions. Xarray correctly raises:

    ValueError: dimensions (...) must have same length as data ndim=1

The synthetic temporal and spatial datasets are now constructed using proper
`xr.DataArray` definitions, which preserves the intent of the test while
aligning with xarray's actual API.
"""

import xarray as xr

from src.features_05 import compute_composites


def _synthetic_temporal_spatial():
    """
    Construct minimal synthetic temporal and spatial IR5 datasets.

    Each dataset contains:
        - 4 timestamps (6‑hourly)
        - 1 latitude
        - 1 longitude
        - 1 variable each (t2m_delta_24h, t2m_laplacian)

    Variables are defined as proper xarray DataArrays with correct dims.
    """

    coords = {
        "time": xr.cftime_range("2000-01-01", periods=4, freq="6H"),
        "lat": [0.0],
        "lon": [0.0],
    }

    temporal = xr.Dataset(
        {
            "t2m_delta_24h": xr.DataArray(
                [0.0, 1.0, 2.0, 3.0],
                dims=("time",),
                coords={"time": coords["time"]},
            )
        },
        coords=coords,
    )

    spatial = xr.Dataset(
        {
            "t2m_laplacian": xr.DataArray(
                [1.0, 1.0, 1.0, 1.0],
                dims=("time",),
                coords={"time": coords["time"]},
            )
        },
        coords=coords,
    )

    return temporal, spatial


def test_composites_formula_evaluation():
    """
    Validate that composite formulas are evaluated correctly.

    For this synthetic case:
        instability_index = t2m_delta_24h * t2m_laplacian

    Since t2m_laplacian = 1.0 for all timesteps,
    the composite should equal t2m_delta_24h exactly.
    """

    temporal, spatial = _synthetic_temporal_spatial()

    cfg = {
        "composites": {
            "instability_index": {
                "temporal": ["t2m_delta_24h"],
                "spatial": ["t2m_laplacian"],
                "formula": "t2m_delta_24h * t2m_laplacian",
            }
        }
    }

    out = compute_composites(temporal, spatial, cfg)

    assert "instability_index" in out.data_vars

    values = out["instability_index"].values
    assert list(values.flatten()) == [0.0, 1.0, 2.0, 3.0]
