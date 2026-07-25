"""
Regression Test – Stage 4 Spatiotemporal Compiler (Aligned with actual Stage 4 code)

Purpose:
    Ensure Stage 4 continues to produce the same outputs for a fixed,
    known synthetic dataset. This protects against:
        - invariant drift
        - shape drift
        - metadata schema changes
        - QC behavior changes
        - contract key changes
        - unexpected interpolation/alignment differences
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


def test_stage4_regression():
    """
    Regression test for Stage 4 invariants.
    """

    # ----------------------------------------------------------------------
    # Synthetic dataset (fixed for regression stability)
    # ----------------------------------------------------------------------
    lat = np.array([0, 1, 2], dtype=float)
    lon = np.array([10, 20], dtype=float)

    time = np.array(
        ["2020-01-01T00:00", "2020-01-01T02:00", "2020-01-01T03:00"],
        dtype="datetime64[ns]",
    )

    temp_data = np.array(
        [
            [[1, 2], [3, 4], [5, 6]],
            [[2, 3], [4, 5], [6, 7]],
            [[9999, 8], [np.nan, 9], [7, 8]],  # outlier  # missing
        ]
    )

    ds_raw = xr.Dataset(
        {"temp": (("time", "lat", "lon"), temp_data)},
        coords={"time": time, "lat": lat, "lon": lon},
    )

    fields = ["temp"]

    # ----------------------------------------------------------------------
    # Stage 4 pipeline
    # ----------------------------------------------------------------------
    ds_grid, grid_contract = grid.process_grid(ds_raw)
    for key in ["lat", "lon", "crs", "lat_ascending", "lon_ascending"]:
        assert key in grid_contract

    ds_masked, mask_contract = mask.process_spatial_consistency(ds_grid, fields)
    assert "mask" in mask_contract

    ds_aligned, temporal_contract = temporal_align.process_temporal_alignment(
        ds_masked, fields
    )
    assert "aligned_time" in temporal_contract

    ds_interpolated, interp_contract = temporal_interpolate.process_interpolation(
        ds_aligned, fields
    )

    ds_stage4 = tensor_builder.process_spatiotemporal_merge(
        ds_interpolated,
        grid_contract,
        mask_contract,
        temporal_contract,
        fields,
    )

    ds_clean, qc_report = qc.process_qc(ds_stage4, fields)

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
        provenance={"source": "regression_test", "stage": "stage4"},
    )

    # ----------------------------------------------------------------------
    # Regression Assertions
    # ----------------------------------------------------------------------

    # R1: Tensor shape must remain stable
    assert ds_clean.temp.shape == (3, 3, 2)

    # R2: No NaNs or outliers remain
    assert not np.isnan(ds_clean.temp.values).any()
    assert np.max(ds_clean.temp.values) < 1e4

    # R3: Time must be evenly spaced
    diffs = np.diff(ds_clean.time.values.astype("datetime64[h]").astype(int))
    assert np.all(diffs == diffs[0])

    # R4: Metadata schema must remain stable
    for key in ["grid", "mask", "qc", "temporal", "tensor", "provenance"]:
        assert key in meta

    # R5: QC report must contain correct keys
    for key in ["qc_pass", "issues", "nan_count", "inf_count", "outlier_count"]:
        assert key in qc_report

    # R6: Tensor metadata shape must match dataset
    assert meta["tensor"]["shape"] == ds_clean.to_array().shape

    # R7: No invariant drift in lat/lon
    assert np.array_equal(ds_clean.lat.values, lat)
    assert np.array_equal(ds_clean.lon.values, lon)
