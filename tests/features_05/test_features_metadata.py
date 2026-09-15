"""
Stage 05 — Metadata Tests
=========================

These tests validate that Stage 05 metadata generation correctly reports
temporal, spatial, and composite feature sections, and that IR4 versioning
information is preserved.

IMPORTANT
---------
The original test fixture used invalid xarray constructs such as:

    ("time", "lat", "lon"), xr.ones((2, 1, 1))

Two issues existed:

1. xarray has **no** `xr.ones` function.
2. The tuple-of-form variable definition is invalid because the number of
   dimensions does not match the number of data dimensions.

The synthetic IR5 dataset is now constructed using proper `xr.DataArray`
definitions, which preserves the intent of the test while aligning with
xarray's actual API.
"""

import json

import numpy as np
import xarray as xr

from src.features_05 import build_metadata


def test_metadata_contains_expected_sections(tmp_path):
    """
    Validate that Stage 05 metadata contains the expected sections:
        - temporal
        - spatial
        - composite
    and that IR4 versioning information is preserved.
    """

    # Proper synthetic IR5 dataset using valid xarray DataArray construction.
    ds = xr.Dataset(
        {
            "t2m_roll_mean_6h": xr.DataArray(
                np.ones((2, 1, 1)),
                dims=("time", "lat", "lon"),
                coords={
                    "time": xr.cftime_range("2000-01-01", periods=2, freq="6H"),
                    "lat": [0.0],
                    "lon": [0.0],
                },
            )
        }
    )

    cfg = {
        "ir4": {"version": "5.0-features"},
        "registry": {
            "temporal": ["t2m_roll_mean_6h"],
            "spatial": [],
            "composite": [],
        },
    }

    metadata = build_metadata(ds, ds, ds, cfg)

    # Validate metadata structure
    assert "temporal" in metadata["layers"]
    assert "spatial" in metadata["layers"]
    assert "composite" in metadata["layers"]

    # Validate IR4 version propagation
    assert metadata["config"]["ir4"]["version"] == "5.0-features"

    # Validate JSON serialization round-trip
    path = tmp_path / "metadata.json"
    path.write_text(json.dumps(metadata))
    loaded = json.loads(path.read_text())
    assert loaded["config"]["ir4"]["version"] == "5.0-features"
