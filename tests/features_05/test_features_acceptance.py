"""
Stage 05 — Acceptance Tests for Temporal, Spatial, and Composite Features
=========================================================================

These tests validate that the Stage 05 feature pipeline produces the expected
set of IR5 features when given a minimal synthetic IR4 tensor.

IMPORTANT
---------
The original test fixture used invalid xarray constructs such as:

    ("time", "lat", "lon"), [280.0, 281.0, 282.0, 283.0]

This is not valid xarray syntax because the number of dimensions does not match
the number of data dimensions. Xarray correctly raises:

    ValueError: dimensions (...) must have same length as data ndim=1

The synthetic IR4 tensor is now constructed using proper `xr.DataArray`
definitions, which preserves the intent of the test while aligning with xarray's
actual API.
"""

import numpy as np
import xarray as xr

from src.features_05 import (
    compute_composites,
    compute_spatial_features,
    compute_temporal_features,
    load_registry,
)


def _synthetic_ir4():
    time = xr.cftime_range("2000-01-01", periods=4, freq="6H")
    lat = [0.0]
    lon = [0.0]

    return xr.Dataset(
        {
            "t2m": xr.DataArray(
                np.array([280.0, 281.0, 282.0, 283.0]).reshape(4, 1, 1),
                dims=("time", "lat", "lon"),
                coords={"time": time, "lat": lat, "lon": lon},
            ),
            "d2m": xr.DataArray(
                np.array([275.0, 276.0, 277.0, 278.0]).reshape(4, 1, 1),
                dims=("time", "lat", "lon"),
                coords={"time": time, "lat": lat, "lon": lon},
            ),
            "u10": xr.DataArray(
                np.ones((4, 1, 1)),
                dims=("time", "lat", "lon"),
                coords={"time": time, "lat": lat, "lon": lon},
            ),
            "v10": xr.DataArray(
                np.ones((4, 1, 1)),
                dims=("time", "lat", "lon"),
                coords={"time": time, "lat": lat, "lon": lon},
            ),
            "msl": xr.DataArray(
                101325.0 * np.ones((4, 1, 1)),
                dims=("time", "lat", "lon"),
                coords={"time": time, "lat": lat, "lon": lon},
            ),
        },
        coords={"time": time, "lat": lat, "lon": lon},
    )


def test_full_feature_stack_matches_registry():
    """
    Validate that the full Stage 05 feature stack (temporal + spatial + composite)
    produces all features listed in the registry.

    This ensures:
        - correct naming conventions
        - correct feature presence
        - correct registry alignment
    """

    ds = _synthetic_ir4()

    cfg = {
        "temporal": {
            "variables": ["t2m"],
            "window_6h": 6,
            "window_24h": 24,
        },
        "spatial": {
            "variables": ["t2m"],
            "kernels": {
                # Minimal kernel to ensure spatial features exist
                "mean_3x3": [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
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

    temporal = compute_temporal_features(ds, cfg)
    spatial = compute_spatial_features(ds, cfg)
    composite = compute_composites(temporal, spatial, cfg)

    registry = load_registry(cfg)

    expected = (
        set(registry["temporal"])
        | set(registry["spatial"])
        | set(registry["composite"])
    )

    present = set(
        list(temporal.data_vars) + list(spatial.data_vars) + list(composite.data_vars)
    )

    assert expected.issubset(present)
