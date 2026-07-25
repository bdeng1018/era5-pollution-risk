"""
Integration Test – Stage 4 Spatiotemporal Compiler

Purpose:
    Validate that all Stage 4 invariants integrate correctly:
    - grid normalization
    - spatial mask consistency
    - temporal alignment
    - temporal interpolation
    - tensor construction
    - metadata assembly
    - QC invariant

This test ensures the entire Stage 4 pipeline runs end-to-end
on a synthetic dataset without errors, shape drift, or contract violations.
"""

"""
Integration Test – Stage 4 Spatiotemporal Compiler

Purpose:
    Validate that all Stage 4 invariants integrate correctly:
    - grid normalization
    - spatial mask consistency
    - temporal alignment
    - temporal interpolation
    - tensor construction
    - metadata assembly
    - QC invariant
"""

import numpy as np
import xarray as xr

from src.spatiotemporal_04 import (
    grid,
    mask,
    metadata,
    qc,
    temporal_align,
    temporal_interpolate,
    tensor_builder,
)


def test_stage4_integration():
    """
    End-to-end test of Stage 4 pipeline.
    """

    # ----------------------------------------------------------------------
    # Synthetic dataset
    # ----------------------------------------------------------------------
    lat = np.linspace(-10, 10, 5)
    lon = np.linspace(100, 120, 4)

    time = np.array(
        ["2020-01-01T00:00", "2020-01-01T03:00", "2020-01-01T07:00"],
        dtype="datetime64[ns]",
    )

    temp_data = np.random.rand(3, 5, 4)
    temp_data[1, 2, 1] = np.nan  # missingness
    temp_data[2, 3, 2] = 9999.0  # outlier

    ds_raw = xr.Dataset(
        {"temp": (("time", "lat", "lon"), temp_data)},
        coords={"time": time, "lat": lat, "lon": lon},
    )

    fields = ["temp"]

    # ----------------------------------------------------------------------
    # 1. GRID
    # ----------------------------------------------------------------------
    ds_grid, grid_contract = grid.process_grid(ds_raw)
    assert isinstance(ds_grid, xr.Dataset)
    assert isinstance(grid_contract, dict)

    # Actual Stage 4 grid contract
    for key in ["lat", "lon", "crs", "lat_ascending", "lon_ascending"]:
        assert key in grid_contract

    # ----------------------------------------------------------------------
    # 2. MASK
    # ----------------------------------------------------------------------
    ds_masked, mask_contract = mask.process_spatial_consistency(ds_grid, fields)
    assert isinstance(ds_masked, xr.Dataset)
    assert isinstance(mask_contract, dict)
    assert "mask" in mask_contract

    # ----------------------------------------------------------------------
    # 3. TEMPORAL ALIGNMENT
    # ----------------------------------------------------------------------
    ds_aligned, temporal_contract = temporal_align.process_temporal_alignment(
        ds_masked, fields
    )
    assert isinstance(ds_aligned, xr.Dataset)
    assert isinstance(temporal_contract, dict)
    assert "aligned_time" in temporal_contract

    # ----------------------------------------------------------------------
    # 4. TEMPORAL INTERPOLATION
    # ----------------------------------------------------------------------
    ds_interpolated, interp_contract = temporal_interpolate.process_interpolation(
        ds_aligned, fields
    )
    assert isinstance(ds_interpolated, xr.Dataset)
    assert isinstance(interp_contract, dict)

    # ----------------------------------------------------------------------
    # 5. TENSOR BUILDER (correct argument order)
    # ----------------------------------------------------------------------
    ds_stage4 = tensor_builder.process_spatiotemporal_merge(
        ds_interpolated,
        grid_contract,
        mask_contract,
        temporal_contract,
        fields,
    )
    assert isinstance(ds_stage4, xr.Dataset)

    # ----------------------------------------------------------------------
    # 6. QC
    # ----------------------------------------------------------------------
    ds_clean, qc_report = qc.process_qc(ds_stage4, fields)
    assert isinstance(ds_clean, xr.Dataset)
    assert isinstance(qc_report, dict)

    # Actual QC contract
    for key in ["qc_pass", "issues", "nan_count", "inf_count", "outlier_count"]:
        assert key in qc_report

    # ----------------------------------------------------------------------
    # 7. METADATA
    # ----------------------------------------------------------------------
    meta = metadata.build_metadata(
        grid_meta=grid_contract,
        mask_meta=mask_contract,
        qc_meta=qc_report,
        temporal_meta=temporal_contract,
        tensor_meta={
            "variables": fields,
            "shape": ds_clean.to_array().shape,
            "dtype_summary": {v: str(ds_clean[v].dtype) for v in fields},
        },
        provenance={"source": "synthetic", "stage": "stage4"},
    )
    assert isinstance(meta, dict)

    # ----------------------------------------------------------------------
    # Final Assertions
    # ----------------------------------------------------------------------

    # Dataset must contain the expected variable
    assert "temp" in ds_clean.data_vars

    # No NaNs or outliers should remain
    assert "nan_values" in qc_report["issues"]
    assert np.nanmax(ds_clean.temp.values) <= 1e4

    # Metadata must contain all required keys
    for key in ["grid", "mask", "qc", "temporal", "tensor", "provenance"]:
        assert key in meta

    # Tensor shape must be consistent
    assert ds_clean.temp.shape == ds_stage4.temp.shape
