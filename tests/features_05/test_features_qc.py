"""
Stage 05 — Quality Control Tests
================================

These tests validate that Stage 05 QC generation correctly reports temporal,
spatial, and composite QC sections, and that QC JSON serialization works.

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

from src.features_05 import build_qc


def test_qc_sections_present(tmp_path):
    """
    Validate that Stage 05 QC contains the expected sections:
        - temporal
        - spatial
        - composite

    and that QC JSON serialization round‑trip works.
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
        "registry": {
            "temporal": ["t2m_roll_mean_6h"],
            "spatial": [],
            "composite": [],
        },
    }

    qc = build_qc(ds, ds, ds, cfg)

    # Validate QC structure (correct path)
    assert "layers" in qc
    assert "temporal" in qc["layers"]
    assert "spatial" in qc["layers"]
    assert "composite" in qc["layers"]

    # Validate JSON serialization round‑trip
    path = tmp_path / "qc.json"
    path.write_text(json.dumps(qc))
    loaded = json.loads(path.read_text())

    assert "layers" in loaded
    assert "temporal" in loaded["layers"]
    assert "spatial" in loaded["layers"]
    assert "composite" in loaded["layers"]
