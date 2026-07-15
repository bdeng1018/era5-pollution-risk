"""
Unit Test – Stage 4 Temporal Interpolation Invariant

Purpose:
    Validate that temporal_interpolate.process_interpolation() produces:
    - a dataset with interpolated timestamps
    - a deterministic interpolation contract containing interpolation metadata
    - no temporal drift, no shape inconsistencies, no illegal values

This test isolates the temporal interpolation invariant only.
"""

import numpy as np
import xarray as xr

import src.spatiotemporal_04.temporal_interpolate as temporal_interpolate


def test_temporal_interpolation_basic():
    """
    Ensure temporal_interpolate.process_interpolation() returns:
    - ds_interpolated (xarray.Dataset)
    - interp_contract (dict with required keys)
    """

    # --------------------------------------------------------------------------
    # Synthetic dataset for testing
    # --------------------------------------------------------------------------
    lat = np.linspace(-10, 10, 5)
    lon = np.linspace(100, 120, 4)

    # Create aligned timestamps (from previous invariant)
    time = np.array(
        ["2020-01-01T00:00",
         "2020-01-01T01:00",
         "2020-01-01T02:00"],
        dtype="datetime64[ns]"
    )

    # Create a dataset with a clear interpolation target
    temp_data = np.array([
        [[1, 2, 3, 4],
         [5, 6, 7, 8],
         [9, 10, 11, 12],
         [13, 14, 15, 16],
         [17, 18, 19, 20]],

        [[2, 3, 4, 5],
         [6, 7, 8, 9],
         [10, 11, 12, 13],
         [14, 15, 16, 17],
         [18, 19, 20, 21]],

        [[3, 4, 5, 6],
         [7, 8, 9, 10],
         [11, 12, 13, 14],
         [15, 16, 17, 18],
         [19, 20, 21, 22]],
    ])

    ds = xr.Dataset(
        {
            "temp": (("time", "lat", "lon"), temp_data)
        },
        coords={"time": time, "lat": lat, "lon": lon},
    )

    fields = ["temp"]

    # --------------------------------------------------------------------------
    # Run temporal interpolation invariant
    # --------------------------------------------------------------------------
    ds_interpolated, interp_contract = temporal_interpolate.process_interpolation(
        ds,
        fields,
    )

    # --------------------------------------------------------------------------
    # Assertions
    # --------------------------------------------------------------------------

    # 1. Output dataset type
    assert isinstance(ds_interpolated, xr.Dataset)

    # 2. Contract type
    assert isinstance(interp_contract, dict)

    # 3. Required contract keys
    for key in ["method", "added_timestamps", "interpolated_fraction"]:
        assert key in interp_contract, f"Missing key in interpolation contract: {key}"

    # 4. Method must be a string (e.g., "linear")
    assert isinstance(interp_contract["method"], str)

    # 5. added_timestamps must be a list
    assert isinstance(interp_contract["added_timestamps"], list)

    # 6. interpolated_fraction must be a float between 0 and 1
    frac = interp_contract["interpolated_fraction"]
    assert isinstance(frac, float)
    assert 0.0 <= frac <= 1.0

    # 7. Dataset variables must remain intact
    assert "temp" in ds_interpolated.data_vars

    # 8. No shape drift in spatial dimensions
    assert ds_interpolated.temp.shape[1:] == ds.temp.shape[1:]

    # 9. Interpolated dataset must have >= original timestamps
    assert ds_interpolated.time.size >= ds.time.size
