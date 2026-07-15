"""
Unit Test – Stage 4 Temporal Alignment Invariant

Purpose:
    Validate that temporal_align.process_temporal_alignment() produces:
    - a dataset with normalized, aligned timestamps
    - a deterministic temporal contract containing alignment metadata
    - no temporal drift, no missing timestamps, no shape inconsistencies

This test isolates the temporal alignment invariant only.
"""

import numpy as np
import xarray as xr

import src.spatiotemporal_04.temporal_align as temporal_align


def test_temporal_alignment_basic():
    """
    Ensure temporal_align.process_temporal_alignment() returns:
    - ds_aligned (xarray.Dataset)
    - temporal_contract (dict with required keys)
    """

    # --------------------------------------------------------------------------
    # Synthetic dataset for testing
    # --------------------------------------------------------------------------
    lat = np.linspace(-10, 10, 5)
    lon = np.linspace(100, 120, 4)

    # Create irregular timestamps
    time = np.array(
        ["2020-01-01T00:00",
         "2020-01-01T03:00",
         "2020-01-01T07:00"],
        dtype="datetime64[ns]"
    )

    temp_data = np.random.rand(3, 5, 4)

    ds = xr.Dataset(
        {
            "temp": (("time", "lat", "lon"), temp_data)
        },
        coords={"time": time, "lat": lat, "lon": lon},
    )

    fields = ["temp"]

    # --------------------------------------------------------------------------
    # Run temporal alignment invariant
    # --------------------------------------------------------------------------
    ds_aligned, temporal_contract = temporal_align.process_temporal_alignment(
        ds,
        fields,
    )

    # --------------------------------------------------------------------------
    # Assertions
    # --------------------------------------------------------------------------

    # 1. Output dataset type
    assert isinstance(ds_aligned, xr.Dataset)

    # 2. Contract type
    assert isinstance(temporal_contract, dict)

    # 3. Required contract keys
    for key in ["aligned_time", "frequency", "missing_timestamps"]:
        assert key in temporal_contract, f"Missing key in temporal contract: {key}"

    # 4. aligned_time must be numpy array
    aligned_time = temporal_contract["aligned_time"]
    assert isinstance(aligned_time, np.ndarray)

    # 5. Frequency must be a string (e.g., "1H")
    assert isinstance(temporal_contract["frequency"], str)

    # 6. Missing timestamps must be a list
    assert isinstance(temporal_contract["missing_timestamps"], list)

    # 7. Aligned dataset must have evenly spaced timestamps
    diffs = np.diff(ds_aligned.time.values.astype("datetime64[h]").astype(int))
    assert np.all(diffs == diffs[0]), "Timestamps are not evenly spaced"

    # 8. Dataset variables must remain intact
    assert "temp" in ds_aligned.data_vars

    # 9. No shape drift in spatial dimensions
    assert ds_aligned.temp.shape[1:] == ds.temp.shape[1:]
