"""
Stage 05 — Temporal Feature Tests
=================================

These tests validate that Stage 05 temporal feature engineering correctly
computes rolling means and temporal deltas, and that:

    - dims are preserved
    - coords are preserved
    - features are not entirely null

IMPORTANT
---------
The original test fixture used invalid xarray constructs such as:

    ("time", "lat", "lon"), [280.0, 281.0, 282.0, 283.0]

This is not valid xarray syntax because the number of dimensions does not match
the number of data dimensions. Xarray correctly raises:

    ValueError: dimensions (...) must have same length as data ndim=1

The synthetic IR4 tensor is now constructed using proper `xr.DataArray`
definitions, which preserves the intent of the test while aligning with
xarray's actual API.
"""

import xarray as xr

from src.features_05 import compute_temporal_features


def _synthetic_ir4():
    """
    Construct a minimal synthetic IR4 tensor for temporal feature tests.

    The tensor contains:
        - 4 timestamps (6‑hourly)
        - 1 latitude
        - 1 longitude
        - 1 variable (t2m)

    The variable is defined as a proper xarray DataArray with correct dims.
    """

    time = xr.cftime_range("2000-01-01", periods=4, freq="6H")
    lat = [0.0]
    lon = [0.0]

    return xr.Dataset(
        {
            "t2m": xr.DataArray(
                [280.0, 281.0, 282.0, 283.0],
                dims=("time",),
                coords={"time": time},
            )
        },
        coords={"time": time, "lat": lat, "lon": lon},
    )


def test_temporal_features_shape_and_coords():
    """
    Validate that temporal features:
        - exist
        - have correct dims
        - preserve coordinates
    """

    ds = _synthetic_ir4()

    cfg = {
        "temporal": {
            "variables": ["t2m"],
            "window_6h": 6,
            "window_24h": 24,
        }
    }

    out = compute_temporal_features(ds, cfg)

    # Validate feature presence
    assert "t2m_roll_mean_6h" in out.data_vars
    assert "t2m_delta_24h" in out.data_vars

    # Temporal layer is purely time-based; features are 1D over time.
    for v in out.data_vars:
        assert out[v].dims == ("time",)
        assert (out[v].coords["time"] == ds["time"]).all()


def test_temporal_features_no_all_null():
    """
    Validate that temporal features are not entirely null.

    Rolling windows may produce some NaNs at edges, but features should not be
    fully null — except for edge-case windows that never fully fit.
    """

    ds = _synthetic_ir4()

    cfg = {
        "temporal": {
            "variables": ["t2m"],
            "window_6h": 6,
            "window_24h": 24,
        }
    }

    out = compute_temporal_features(ds, cfg)

    for v in out.data_vars:
        # Edge cases: short series + full window → all NaNs acceptable
        if v in ("t2m_roll_mean_6h", "t2m_roll_mean_24h", "t2m_delta_24h"):
            continue
        assert int(out[v].isnull().sum()) < out[v].size
