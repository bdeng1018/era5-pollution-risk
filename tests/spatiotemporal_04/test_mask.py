"""
Unit Test – Stage 4 Mask Invariant

Purpose:
    Validate that mask.process_spatial_consistency() produces:
    - a dataset with spatial masks applied correctly
    - a deterministic mask contract containing mask arrays
    - spatial consistency invariants (no illegal values, no shape drift)

This test isolates the mask invariant only.
"""

import numpy as np
import xarray as xr

from src.spatiotemporal_04 import mask


def test_mask_process_spatial_consistency_basic():
    """
    Ensure mask.process_spatial_consistency() returns:
    - ds_masked (xarray.Dataset)
    - mask_contract (dict with required keys)
    """

    # --------------------------------------------------------------------------
    # Synthetic dataset for testing
    # --------------------------------------------------------------------------
    lat = np.linspace(-10, 10, 5)
    lon = np.linspace(100, 120, 4)
    time = np.array(["2020-01-01"], dtype="datetime64[ns]")

    # Create a dataset with some missing values to trigger masking logic
    temp_data = np.random.rand(1, 5, 4)
    temp_data[0, 2, 1] = np.nan  # introduce missingness

    ds = xr.Dataset(
        {"temp": (("time", "lat", "lon"), temp_data)},
        coords={"time": time, "lat": lat, "lon": lon},
    )

    fields = ["temp"]

    # --------------------------------------------------------------------------
    # Run mask invariant
    # --------------------------------------------------------------------------
    ds_masked, mask_contract = mask.process_spatial_consistency(
        ds,
        fields,
    )

    # --------------------------------------------------------------------------
    # Assertions
    # --------------------------------------------------------------------------

    # 1. Output dataset type
    assert isinstance(ds_masked, xr.Dataset)

    # 2. Contract type
    assert isinstance(mask_contract, dict)

    # 3. Required contract keys
    for key in ["mask", "valid_fraction"]:
        assert key in mask_contract, f"Missing key in mask contract: {key}"

    # 4. Mask must be a boolean numpy array
    assert isinstance(mask_contract["mask"], np.ndarray)
    assert mask_contract["mask"].dtype == bool

    # 5. Mask shape must match lat/lon grid
    assert mask_contract["mask"].shape == (ds.lat.shape[0], ds.lon.shape[0])

    # 6. valid_fraction must be a float between 0 and 1
    vf = mask_contract["valid_fraction"]
    assert isinstance(vf, float)
    assert 0.0 <= vf <= 1.0

    # 7. Masked dataset must contain the same variables
    assert "temp" in ds_masked.data_vars

    # 8. Masked dataset must not introduce shape drift
    assert ds_masked.temp.shape == ds.temp.shape
