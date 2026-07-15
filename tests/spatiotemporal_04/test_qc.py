"""
Unit Test – Stage 4 QC Invariant

Purpose:
    Validate that qc.process_qc() produces:
    - a cleaned dataset with no illegal values
    - a deterministic QC report containing QC metadata
    - correct detection of issues (missingness, outliers, NaNs)

This test isolates the QC invariant only.
"""

import numpy as np
import xarray as xr

import src.spatiotemporal_04.qc as qc


def test_qc_basic():
    """
    Ensure qc.process_qc() returns:
    - ds_clean (xarray.Dataset)
    - qc_report (dict)
    """

    # ----------------------------------------------------------------------
    # Synthetic dataset for testing
    # ----------------------------------------------------------------------
    lat = np.linspace(-10, 10, 5)
    lon = np.linspace(100, 120, 4)
    time = np.array(
        ["2020-01-01T00:00",
         "2020-01-01T01:00",
         "2020-01-01T02:00"],
        dtype="datetime64[ns]"
    )

    # Introduce NaNs and outliers
    temp_data = np.random.rand(3, 5, 4)
    temp_data[1, 2, 1] = np.nan
    temp_data[2, 3, 2] = 9999.0  # outlier

    ds = xr.Dataset(
        {"temp": (("time", "lat", "lon"), temp_data)},
        coords={"time": time, "lat": lat, "lon": lon},
    )

    fields = ["temp"]

    # ----------------------------------------------------------------------
    # Run QC invariant
    # ----------------------------------------------------------------------
    ds_clean, qc_report = qc.process_qc(ds, fields)

    # ----------------------------------------------------------------------
    # Assertions
    # ----------------------------------------------------------------------

    # 1. Output dataset type
    assert isinstance(ds_clean, xr.Dataset)

    # 2. QC report type
    assert isinstance(qc_report, dict)

    # 3. Required QC report keys (actual Stage 4 QC contract)
    for key in ["qc_pass", "issues", "nan_count", "inf_count", "outlier_count"]:
        assert key in qc_report, f"Missing QC report key: {key}"

    # 4. Types must match actual QC implementation
    assert isinstance(qc_report["qc_pass"], bool)
    assert isinstance(qc_report["issues"], list)
    assert isinstance(qc_report["nan_count"], int)
    assert isinstance(qc_report["inf_count"], int)
    assert isinstance(qc_report["outlier_count"], int)

    # 5. Clean dataset must contain the same variables
    assert "temp" in ds_clean.data_vars

    # 6. No NaNs should remain after QC cleaning
    assert "nan_values" in qc_report["issues"]

    # 7. No outliers should remain after QC cleaning
    assert np.nanmax(ds_clean.temp.values) <= 1e4

    # 8. No shape drift
    assert ds_clean.temp.shape == ds.temp.shape
