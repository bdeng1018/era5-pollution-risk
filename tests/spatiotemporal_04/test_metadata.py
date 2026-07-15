"""
Unit Test – Stage 4 Metadata Invariant

Purpose:
    Validate that metadata.build_metadata() produces:
    - a deterministic metadata dictionary
    - schema-consistent keys
    - correct types for each metadata field
    - no missing keys, no illegal values
"""

import numpy as np

import src.spatiotemporal_04.metadata as metadata


def test_metadata_build_basic():
    """
    Validate metadata.build_metadata() schema.
    """

    # ----------------------------------------------------------------------
    # Synthetic contracts matching actual Stage 4 implementation
    # ----------------------------------------------------------------------
    grid_meta = {
        "lat": np.linspace(-10, 10, 5),
        "lon": np.linspace(100, 120, 4),
        "crs": "EPSG:4326",
    }

    mask_meta = {
        "mask": np.ones((5, 4), dtype=bool),
        "valid_fraction": 1.0,
    }

    qc_meta = {
        "qc_pass": True,
        "issues": [],
        "nan_count": 0,
        "inf_count": 0,
        "outlier_count": 0,
        "zero_fields": [],
        "constant_fields": [],
        "physical_range_violations": {},
        "temporal_jumps": {},
        "spatial_jumps": {},
    }


    temporal_meta = {
        "aligned_time": np.array(
            ["2020-01-01T00:00",
             "2020-01-01T01:00",
             "2020-01-01T02:00"],
            dtype="datetime64[ns]"
        ),
        "frequency": "1H",
        "missing_timestamps": [],
    }

    tensor_meta = {
        "variables": ["temp"],
        "shape": (3, 5, 4),
        "dtype_summary": {"temp": "float64"},
    }

    provenance = {
        "source": "synthetic.nc",
        "stage": "stage4",
    }

    # ----------------------------------------------------------------------
    # Build metadata
    # ----------------------------------------------------------------------
    meta = metadata.build_metadata(
        grid_meta=grid_meta,
        mask_meta=mask_meta,
        qc_meta=qc_meta,
        temporal_meta=temporal_meta,
        tensor_meta=tensor_meta,
        provenance=provenance,
    )

    # ----------------------------------------------------------------------
    # Assertions
    # ----------------------------------------------------------------------
    assert isinstance(meta, dict)

    for key in ["grid", "mask", "qc", "temporal", "tensor", "provenance"]:
        assert key in meta

    # Grid
    assert isinstance(meta["grid"]["lat"], np.ndarray)
    assert isinstance(meta["grid"]["lon"], np.ndarray)
    assert meta["grid"]["crs"] == "EPSG:4326"

    # Mask
    assert meta["mask"]["valid_fraction"] == 1.0

    # QC
    for key in ["qc_pass", "issues", "nan_count", "outlier_count", "inf_count"]:
        assert key in meta["qc"]

    # Temporal
    assert meta["temporal"]["frequency"] == "1H"

    # Tensor
    assert meta["tensor"]["shape"] == (3, 5, 4)
    assert meta["tensor"]["dtype_summary"] == {"temp": "float64"}

    # Provenance
    assert meta["provenance"]["stage"] == "stage4"
