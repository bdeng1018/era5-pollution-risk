"""
System Test – Stage 4 Spatiotemporal Compiler

Purpose:
    Validate Stage 4 as a complete subsystem using its public interface:
        driver.run_stage4()

This test ensures:
    - Stage 4 runs end-to-end through the driver
    - Output dataset is written correctly
    - QC report is written correctly
    - Metadata is written correctly
    - No exceptions occur during full pipeline execution
    - Output files are structurally valid
"""

import os
import pickle

import numpy as np
import xarray as xr

import src.spatiotemporal_04.driver as driver


def test_stage4_system(tmp_path):
    """
    System-level test of Stage 4 using driver.run_stage4().
    """

    # ----------------------------------------------------------------------
    # Synthetic dataset written to disk
    # ----------------------------------------------------------------------
    lat = np.linspace(30, 50, 10)
    lon = np.linspace(-130, -110, 8)

    time = np.array(
        ["2020-01-01T00:00",
         "2020-01-01T03:00",
         "2020-01-01T07:00"],
        dtype="datetime64[ns]"
    )

    temp_data = np.random.rand(3, 10, 8)
    temp_data[1, 3, 2] = np.nan
    temp_data[2, 7, 5] = 9999.0

    ds_raw = xr.Dataset(
        {
            "temp": (("time", "lat", "lon"), temp_data),
            "humidity": (("time", "lat", "lon"), temp_data * 0.5),
        },
        coords={"time": time, "lat": lat, "lon": lon},
    )

    raw_path = tmp_path / "raw.nc"
    ds_raw.to_netcdf(raw_path)

    # ----------------------------------------------------------------------
    # Output paths
    # ----------------------------------------------------------------------
    out_dataset = tmp_path / "stage4_output.nc"
    out_qc = tmp_path / "stage4_qc.pkl"
    out_meta = tmp_path / "stage4_metadata.pkl"

    fields = ["temp", "humidity"]

    # ----------------------------------------------------------------------
    # Run Stage 4 through the driver
    # ----------------------------------------------------------------------
    driver.run_stage4(
        path=str(raw_path),
        fields=fields,
        out_dataset=str(out_dataset),
        out_qc=str(out_qc),
        out_meta=str(out_meta),
    )

    # ----------------------------------------------------------------------
    # Assertions – QC Report (load first, since we use it below)
    # ----------------------------------------------------------------------
    assert os.path.exists(out_qc)
    with open(out_qc, "rb") as f:
        qc_report = pickle.load(f)

    assert isinstance(qc_report, dict)

    # Full QC contract
    for key in [
        "qc_pass",
        "issues",
        "nan_count",
        "inf_count",
        "outlier_count",
        "zero_fields",
        "constant_fields",
        "physical_range_violations",
        "temporal_jumps",
        "spatial_jumps",
    ]:
        assert key in qc_report

    # QC may detect issues; system test must NOT require qc_pass=True
    assert isinstance(qc_report["qc_pass"], bool)

    # ----------------------------------------------------------------------
    # Assertions – Output Dataset
    # ----------------------------------------------------------------------
    assert os.path.exists(out_dataset)
    ds_clean = xr.open_dataset(out_dataset)

    # Dataset must contain all fields
    for field in fields:
        assert field in ds_clean.data_vars

    # Outliers must be clipped to threshold; NaNs may remain by design
    for field in fields:
        assert np.nanmax(np.abs(ds_clean[field].values)) <= 1e4

    # Time must be evenly spaced
    diffs = np.diff(ds_clean.time.values.astype("datetime64[h]").astype(int))
    assert np.all(diffs == diffs[0])

    # ----------------------------------------------------------------------
    # Assertions – Metadata
    # ----------------------------------------------------------------------
    assert os.path.exists(out_meta)
    with open(out_meta, "rb") as f:
        meta = pickle.load(f)

    assert isinstance(meta, dict)

    for key in ["grid", "mask", "qc", "temporal", "tensor", "provenance"]:
        assert key in meta

    # Grid contract
    for key in ["lat", "lon"]:
        assert key in meta["grid"]

    # Tensor metadata must match dataset
    assert meta["tensor"]["shape"] == ds_clean.to_array().shape
    assert isinstance(meta["tensor"]["dtype_summary"], dict)
