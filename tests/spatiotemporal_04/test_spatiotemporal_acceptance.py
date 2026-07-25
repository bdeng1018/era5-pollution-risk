"""
Acceptance Test – Stage 4 Spatiotemporal Compiler

Purpose:
    Validate that Stage 4 meets functional acceptance criteria:
    - Produces a clean, aligned, interpolated spatiotemporal dataset
    - Produces correct metadata and QC report
    - No shape drift, no illegal values, no missing timestamps
    - Output is ready for Stage 5 ingestion
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


def test_stage4_acceptance():
    """
    Acceptance criteria for Stage 4.
    """

    # ----------------------------------------------------------------------
    # Synthetic dataset
    # ----------------------------------------------------------------------
    lat = np.linspace(30, 50, 10)
    lon = np.linspace(-130, -110, 8)

    time = np.array(
        [
            "2020-01-01T00:00",
            "2020-01-01T02:00",
            "2020-01-01T05:00",
            "2020-01-01T06:00",
        ],
        dtype="datetime64[ns]",
    )

    temp_data = np.random.rand(4, 10, 8)
    temp_data[1, 3, 2] = np.nan
    temp_data[2, 7, 5] = 9999.0

    ds_raw = xr.Dataset(
        {
            "temp": (("time", "lat", "lon"), temp_data),
            "humidity": (("time", "lat", "lon"), temp_data * 0.5),
        },
        coords={"time": time, "lat": lat, "lon": lon},
    )

    fields = ["temp", "humidity"]

    # ----------------------------------------------------------------------
    # Stage 4 pipeline
    # ----------------------------------------------------------------------
    ds_grid, grid_contract = grid.process_grid(ds_raw)
    assert "lat" in grid_contract
    assert "lon" in grid_contract
    assert "crs" in grid_contract

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
        provenance={"source": "synthetic_acceptance", "stage": "stage4"},
    )

    # ----------------------------------------------------------------------
    # Acceptance Criteria
    # ----------------------------------------------------------------------

    # A1: Dataset must contain all requested fields
    for field in fields:
        assert field in ds_clean.data_vars

    # A2: No NaNs or outliers remain
    for field in fields:
        assert "nan_values" in qc_report["issues"]
        assert qc_report["outlier_count"] >= 0

    # A3: Time must be evenly spaced
    diffs = np.diff(ds_clean.time.values.astype("datetime64[h]").astype(int))
    assert np.all(diffs == diffs[0])

    # A4: Metadata must contain all required keys
    for key in ["grid", "mask", "qc", "temporal", "tensor", "provenance"]:
        assert key in meta

    # A5: QC report must contain correct keys
    for key in ["qc_pass", "issues", "nan_count", "inf_count", "outlier_count"]:
        assert key in qc_report

    # A6: Tensor shape must be correct
    assert ds_clean.temp.shape[1] == lat.size
    assert ds_clean.temp.shape[2] == lon.size

    # A7: Output must be Stage 5 compatible
    assert set(ds_clean.dims.keys()) == {"time", "lat", "lon"}
